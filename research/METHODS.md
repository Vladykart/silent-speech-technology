# Research method and evidence policy

**Research freeze for deck/landscape claims:** 2026-07-28. Official Gaddy model/data records were re-verified for the local replay bench on 2026-07-31; all other links use the earlier date unless a row says otherwise.

## Method

1. The captain-supplied Moshi URL was retrieved once by bounded direct HTTPS; provenance and limitations are in `../provenance/source-record.md`.
2. Repository structure, demo, and product boundaries were developed independently while a parallel scout prepared an evidence report.
3. Before research/deck finalization, the 651-line scout report (SHA-256 `465ecdca024a3864e001f785124afb99a6ac1c1296b192e747d491c65a04dcee`) was read in full and critically reconciled in [`scout-review.md`](scout-review.md). Load-bearing SilentWear, MONA/LISA, Meta, licence, patent, UAE-law and EU-law claims were checked against direct arXiv HTML, DOI/publisher/institutional pages, official law/company pages, registries, or GitHub exact commits where feasible.
4. Corporate material is classified as marketing/announcement, never independent product validation. Preprints are not called peer reviewed. A dataset or repository license does not imply clinical, patent, data-subject, or commercial rights.
5. No paper, model, dataset, participant sample, third-party slide, font, image, or upstream clone is committed. For `realtime/`, official Gaddy model/data assets are checksum-verified into git-ignored local storage and selected arrays are replayed under CC BY 4.0; exact IDs/hashes/notices are in `realtime/`. GitHub evidence was inspected through `gh-axi`; exact commits are recorded.

## Evidence hierarchy

For technical claims, prefer: peer-reviewed paper at publisher/DOI + accessible full text → registry metadata + institutional manuscript → preprint. For product status: regulator/registry → official trial record → company release/manual → reputable reporting. Company assertions do not establish independent replication.

## Performance-number policy

Every performance number must identify source, participants, modality, task/vocabulary, personalization/session condition, metric, and non-transfer boundary. Missing values remain missing. WER means `(substitutions + deletions + insertions) / reference words`; it can exceed 100% and depends on normalization, decoder, language model, vocabulary, and test set. “Accuracy” is not substituted for WER.

## Link checks

`research/intake/url-check-2026-07-28.tsv` is a bounded reachability snapshot, not proof of content correctness. A `200`, `206`, `302`, `403`, or bot challenge can still leave metadata usable or content unverified. Some DOI targets attempted insecure HTTP redirects and were not followed because retrieval required HTTPS. Local references are checked with `python3 tools/validate_project.py`.

## Known QA limits

- Browser-rendered review was unavailable; no visual/browser certification is claimed.
- Paywalls, bot defenses, and inaccessible full text limited some checks.
- No systematic review protocol, meta-analysis, patent freedom-to-operate opinion, regulatory opinion, market-sizing study, or user discovery was performed.
- Search was deliberately bounded rather than exhaustive. The landscape should be refreshed before external decisions.
