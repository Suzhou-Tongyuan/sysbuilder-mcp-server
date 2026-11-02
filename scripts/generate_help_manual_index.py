"""Generate a deterministic, page-addressable text index for the Sysbuilder user manual."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


def _clean_page_text(raw: str) -> str:
    text = unicodedata.normalize("NFKC", (raw or "").replace("\x00", "")).replace("\r\n", "\n")
    lines: list[str] = []
    blank = False
    for raw_line in text.splitlines():
        line = re.sub(r"[\t \u00a0]+", " ", raw_line).strip()
        if not line:
            if lines and not blank:
                lines.append("")
            blank = True
            continue
        lines.append(line)
        blank = False
    return "\n".join(lines).strip()


def generate_index(source: Path, output: Path) -> dict[str, object]:
    source = source.resolve()
    output = output.resolve()
    reader = PdfReader(str(source), strict=False)
    pages = [
        {"page": page_number, "text": _clean_page_text(page.extract_text() or "")}
        for page_number, page in enumerate(reader.pages, start=1)
    ]
    total_chars = sum(len(str(page["text"])) for page in pages)
    if len(pages) < 10 or total_chars < 10_000:
        raise RuntimeError(f"manual extraction is unexpectedly small: pages={len(pages)}, chars={total_chars}")

    payload: dict[str, object] = {
        "format_version": 1,
        "title": "MWORKS.Sysbuilder 用户手册",
        "source_pdf": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "page_count": len(pages),
        "total_chars": total_chars,
        "pages": pages,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Sysbuilder help-manual search index")
    parser.add_argument("--input", required=True, type=Path, help="Sysbuilder user manual PDF")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON index")
    args = parser.parse_args()
    payload = generate_index(args.input, args.output)
    print(
        f"generated {args.output}: pages={payload['page_count']}, chars={payload['total_chars']}, "
        f"sha256={payload['source_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
