#!/usr/bin/env python3
"""Download remote dasoftn.in PDF links into local mirror folder and rewrite HTML links."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

PDF_URL_RE = re.compile(r"https?://www\.dasoftn\.in/wp-content/uploads/[^\"'\s<>]+?\.pdf", re.IGNORECASE)


def request_url(pdf_url: str) -> str:
    parsed = urlparse(pdf_url)
    safe_path = quote(unquote(parsed.path), safe='/%._-()[]')
    safe_query = quote(unquote(parsed.query), safe='=&%._-')
    return parsed._replace(path=safe_path, query=safe_query).geturl()


def normalized_upload_path(pdf_url: str) -> Path:
    parsed = urlparse(pdf_url)
    raw_path = parsed.path.lstrip("/")
    # decode each path segment while keeping directory structure
    segments = [unquote(part) for part in raw_path.split("/") if part]
    return Path(*segments)


def download_pdf(url: str, dest: Path, timeout: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(request_url(url), headers={"User-Agent": "Mozilla/5.0 (pdf-mirror-bot)"})
    with urlopen(req, timeout=timeout) as response:
        data = response.read()
    dest.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="cloned-site/www.dasoftn.in", help="Path to mirrored site root")
    parser.add_argument("--timeout", type=int, default=45, help="Download timeout seconds per file")
    parser.add_argument("--limit", type=int, default=0, help="Optional cap for number of PDFs to download (0 = all)")
    parser.add_argument("--fail-on-errors", action="store_true", help="Exit non-zero if any PDF download fails")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root directory does not exist: {root}", file=sys.stderr)
        return 1

    html_files = sorted(root.rglob("*.html"))
    url_to_target: dict[str, Path] = {}
    html_url_refs: dict[Path, set[str]] = {}

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        urls = set(PDF_URL_RE.findall(text))
        if urls:
            html_url_refs[html_file] = urls
            for url in urls:
                uploads_path = normalized_upload_path(url)
                url_to_target[url] = root / "mirror-pdfs" / uploads_path

    unique_urls = sorted(url_to_target.keys())
    if args.limit > 0:
        unique_urls = unique_urls[: args.limit]

    print(f"Found {len(url_to_target)} unique PDF links across {len(html_url_refs)} HTML files")
    if args.limit > 0:
        print(f"Applying --limit={args.limit}; processing {len(unique_urls)} URLs")

    downloaded = 0
    failed: list[tuple[str, str]] = []
    for url in unique_urls:
        dest = url_to_target[url]
        try:
            if not dest.exists() or dest.stat().st_size == 0:
                download_pdf(url, dest, timeout=args.timeout)
            downloaded += 1
            print(f"OK {url} -> {dest.relative_to(root)}")
        except Exception as exc:  # noqa: BLE001
            failed.append((url, str(exc)))
            print(f"FAIL {url} :: {exc}", file=sys.stderr)

    # rewrite links in HTML only for URLs we successfully mirrored
    rewritten_files = 0
    successful = {url for url in unique_urls if url not in {u for u, _ in failed}}
    for html_file, urls in html_url_refs.items():
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        original = text
        for url in sorted(urls):
            if url not in successful:
                continue
            target = url_to_target[url]
            rel = os.path.relpath(target, start=html_file.parent).replace(os.sep, "/")
            text = text.replace(url, rel)
        if text != original:
            html_file.write_text(text, encoding="utf-8")
            rewritten_files += 1

    print(f"Downloaded {downloaded} PDFs")
    print(f"Rewrote links in {rewritten_files} HTML files")
    if failed:
        print(f"Failed to fetch {len(failed)} PDFs", file=sys.stderr)
        if args.fail_on_errors:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
