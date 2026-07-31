"""Relative-position Transformer used by the released dgaddy checkpoint.

Adapted from ``transformer.py`` in dgaddy/silent_speech at commit
``a89357c2086609b432919b9d14ffc0be5d8983d5`` under the MIT License.
Copyright (c) 2021 David Gaddy. The full notice is in THIRD_PARTY_NOTICES.md.
"""
from __future__ import annotations

from typing import Optional

import torch
from torch import nn
import torch.nn.functional as functional


class TransformerEncoderLayer(nn.Module):
    """Upstream-compatible encoder layer and state-dict key layout."""

    def __init__(
        self,
        d_model: int,
        nhead: int,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        relative_positional: bool = True,
        relative_positional_distance: int = 100,
    ) -> None:
        super().__init__()
        self.self_attn = MultiHeadAttention(
            d_model,
            nhead,
            dropout=dropout,
            relative_positional=relative_positional,
            relative_positional_distance=relative_positional_distance,
        )
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.activation = nn.ReLU()

    def forward(
        self,
        source: torch.Tensor,
        src_mask: Optional[torch.Tensor] = None,
        src_key_padding_mask: Optional[torch.Tensor] = None,
        is_causal: bool = False,
    ) -> torch.Tensor:
        del src_mask, src_key_padding_mask, is_causal
        update = self.self_attn(source)
        source = self.norm1(source + self.dropout1(update))
        update = self.linear2(self.dropout(self.activation(self.linear1(source))))
        return self.norm2(source + self.dropout2(update))


class MultiHeadAttention(nn.Module):
    def __init__(
        self,
        d_model: int = 256,
        n_head: int = 4,
        dropout: float = 0.1,
        relative_positional: bool = True,
        relative_positional_distance: int = 100,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_head = n_head
        self.d_qkv = d_model // n_head
        if self.d_qkv * n_head != d_model:
            raise ValueError("d_model must be divisible by n_head")
        self.w_q = nn.Parameter(torch.empty(n_head, d_model, self.d_qkv))
        self.w_k = nn.Parameter(torch.empty(n_head, d_model, self.d_qkv))
        self.w_v = nn.Parameter(torch.empty(n_head, d_model, self.d_qkv))
        self.w_o = nn.Parameter(torch.empty(n_head, self.d_qkv, d_model))
        for parameter in (self.w_q, self.w_k, self.w_v, self.w_o):
            nn.init.xavier_normal_(parameter)
        self.dropout = nn.Dropout(dropout)
        self.relative_positional = (
            LearnedRelativePositionalEmbedding(relative_positional_distance, n_head, self.d_qkv, True)
            if relative_positional
            else None
        )

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        query = torch.einsum("tbf,hfa->bhta", value, self.w_q)
        key = torch.einsum("tbf,hfa->bhta", value, self.w_k)
        projected_value = torch.einsum("tbf,hfa->bhta", value, self.w_v)
        logits = torch.einsum("bhqa,bhka->bhqk", query, key) / (self.d_qkv**0.5)
        if self.relative_positional is not None:
            positional_query = query.permute(2, 0, 1, 3)
            length, batch, heads, depth = positional_query.size()
            position_logits, _ = self.relative_positional(
                positional_query.reshape(length, batch * heads, depth)
            )
            logits = logits + position_logits.view(batch, heads, length, length)
        probabilities = self.dropout(functional.softmax(logits, dim=-1))
        attended = torch.einsum("bhqk,bhka->bhqa", probabilities, projected_value)
        return torch.einsum("bhta,haf->tbf", attended, self.w_o)


class LearnedRelativePositionalEmbedding(nn.Module):
    """Upstream learned relative-position implementation (fairseq-derived)."""

    def __init__(
        self,
        max_relative_pos: int,
        num_heads: int,
        embedding_dim: int,
        unmasked: bool = False,
        heads_share_embeddings: bool = False,
        add_to_values: bool = False,
    ) -> None:
        super().__init__()
        self.max_relative_pos = max_relative_pos
        self.num_heads = num_heads
        self.embedding_dim = embedding_dim
        self.unmasked = unmasked
        self.heads_share_embeddings = heads_share_embeddings
        self.add_to_values = add_to_values
        count = 2 * max_relative_pos - 1 if unmasked else max_relative_pos
        size = (
            [count, embedding_dim, 1]
            if heads_share_embeddings
            else [num_heads, count, embedding_dim, 1]
        )
        if add_to_values:
            size[-1] = 2
        self.embeddings = nn.Parameter(torch.zeros(*size))
        nn.init.normal_(self.embeddings, mean=0.0, std=embedding_dim**-0.5)

    def forward(self, query: torch.Tensor, saved_state=None):
        if saved_state is not None and "prev_key" in saved_state:
            if self.unmasked:
                raise ValueError("cached state is only valid for decoder attention")
            length = saved_state["prev_key"].shape[-2] + 1
            decoder_step = True
        else:
            length = query.shape[0]
            decoder_step = False
        embeddings = self.get_embeddings_for_query(length)
        values = embeddings[..., 1] if self.add_to_values else None
        logits = self.calculate_positional_logits(query, embeddings[..., 0])
        return self.relative_to_absolute_indexing(logits, decoder_step), values

    def get_embeddings_for_query(self, length: int) -> torch.Tensor:
        pad_length = max(length - self.max_relative_pos, 0)
        start = max(self.max_relative_pos - length, 0)
        if self.unmasked:
            with torch.no_grad():
                padded = functional.pad(self.embeddings, (0, 0, 0, 0, pad_length, pad_length))
            return padded.narrow(-3, start, 2 * length - 1)
        with torch.no_grad():
            padded = functional.pad(self.embeddings, (0, 0, 0, 0, pad_length, 0))
        return padded.narrow(-3, start, length)

    def calculate_positional_logits(
        self, query: torch.Tensor, relative_embeddings: torch.Tensor
    ) -> torch.Tensor:
        if self.heads_share_embeddings:
            logits = torch.einsum("lbd,md->lbm", query, relative_embeddings)
        else:
            query = query.view(query.shape[0], -1, self.num_heads, self.embedding_dim)
            logits = torch.einsum("lbhd,hmd->lbhm", query, relative_embeddings)
            logits = logits.contiguous().view(logits.shape[0], -1, logits.shape[-1])
        length = query.size(0)
        if length > self.max_relative_pos:
            pad_length = length - self.max_relative_pos
            logits[:, :, :pad_length] -= 1e8
            if self.unmasked:
                logits[:, :, -pad_length:] -= 1e8
        return logits

    def relative_to_absolute_indexing(self, value: torch.Tensor, decoder_step: bool) -> torch.Tensor:
        length, batch_heads, _ = value.shape
        if decoder_step:
            return value.contiguous().view(batch_heads, 1, -1)
        if self.unmasked:
            value = functional.pad(value, (0, 1)).transpose(0, 1)
            value = value.contiguous().view(batch_heads, length * 2 * length)
            value = functional.pad(value, (0, length - 1))
            value = value.view(batch_heads, length + 1, 2 * length - 1)
            return value[:, :length, length - 1 :]
        value = functional.pad(value, (1, 0)).transpose(0, 1)
        value = value.contiguous().view(batch_heads, length + 1, length)
        return value[:, 1:, :]
