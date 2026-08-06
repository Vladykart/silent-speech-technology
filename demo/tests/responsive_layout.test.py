#!/usr/bin/env python3
"""Regression test for the tablet stacking invariant that prevents clipped columns."""
from __future__ import annotations

from pathlib import Path
import re

CSS = (Path(__file__).resolve().parents[1] / "styles.css").read_text()


def media_blocks(css: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    pattern = re.compile(r"@media\s*\(max-width:\s*(\d+)px\)\s*\{")
    for match in pattern.finditer(css):
        depth = 1
        cursor = match.end()
        while cursor < len(css) and depth:
            if css[cursor] == "{":
                depth += 1
            elif css[cursor] == "}":
                depth -= 1
            cursor += 1
        if depth:
            raise AssertionError(f"unclosed media block at {match.start()}")
        blocks.append((int(match.group(1)), css[match.end():cursor - 1]))
    return blocks


def main() -> None:
    required = (
        ".hero { grid-template-columns: 1fr;",
        ".walkthrough { grid-template-columns: 1fr;",
        ".walkthrough ol { grid-template-columns: 1fr;",
        ".truth-strip { grid-template-columns: 1fr;",
        ".demo-grid { display: block;",
        ".decision-panel { display: block;",
    )
    tablet_blocks = [
        (width, block)
        for width, block in media_blocks(CSS)
        if width >= 1024 and all(fragment in block for fragment in required)
    ]
    assert tablet_blocks, "1024px landscape must use the complete stacked layout"
    assert not re.search(r"(?:html|body|\*)\s*\{[^}]*overflow-x\s*:\s*hidden", CSS, re.S), (
        "page overflow must be corrected causally, not hidden globally"
    )
    print(f"responsive layout test passed: complete stacking begins at {tablet_blocks[0][0]}px")


if __name__ == "__main__":
    main()
