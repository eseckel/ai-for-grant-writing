"""Small script to parse and validate README.md into a proper index.md
"""

import argparse
import os
import pathlib
import re
import sys
import urllib.request

from urllib.parse import urlparse


INDEX_MD_PATH = pathlib.Path("docs") / "index.md"


# URL validation code
class NoRedirection(urllib.request.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response


def validate_single_url(url):
    """Checks if a url is valid by querying it."""

    # First do a quick syntax check
    try:
        r = urlparse(url)
    except Exception:
        raise Exception(f"Failed to parse URL: {url}")
    else:
        if not r.scheme or not r.netloc:
            # is it a path?
            if os.path.exists(url):
                return
            raise Exception(f"URL appears to be mal-formatted: {url}")

    # Now do a quick check to see if the page actually exists
    try:
        opener = urllib.request.build_opener(NoRedirection)
        req = urllib.request.Request(url, method="HEAD")
        with opener.open(req) as response:
            _ = response.read(10)
    except Exception:
        raise Exception(f"URL cannot be reached: {url}")


def validate_all_urls(lines):
    """Search and validate URLs in a set of lines."""

    # Collect headers for markdown link validation
    headers = set()
    for ln in lines:
        if ln.lstrip().startswith("#"):
            url = ln.replace("#", "").strip().replace(" ", "-").lower()
            headers.add(url)

    re_url = re.compile(r"\[[\w\s']+\]\((.+)\)")

    failed = False
    for ix, ln in enumerate(lines, start=1):
        m = re_url.search(ln)
        if m:
            url = m.group(1)
            if url.startswith("#"):  # Markdown URL
                if url[1:] not in headers:
                    print(f"Markdown link on line {ix} is not valid: {url}")
                    failed = True
            else:
                try:
                    _ = validate_single_url(url)
                except Exception as err:
                    print(f"URL validation failed on line {ix}: {err}")
                    failed = True
    if failed:
        sys.exit(1)  # abort


def filter_gh_toc(lines):
    """Filter the TOC for GitHub that should not be rendered in HTML."""
    # TOC is the first listing before we hit any level 2 header (##)
    ignore_lists = True
    for ln in lines:
        if ln.startswith("##"):  # level 2, 3, ... headers
            ignore_lists = False
        elif ln.lstrip().startswith("-"):  # is list
            if ignore_lists:
                continue
        yield ln


def add_toc_depth_limit():
    yield from ["---", "toc_depth: 3", "---"]


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("readme",
                    type=pathlib.Path,
                    help="File to process, e.g. README.md")
    ap.add_argument("--validate-only",
                    action="store_true",
                    help="Only validate URLs.")
    args = ap.parse_args()

    # Read input file into memory.
    with open(args.readme) as handle:
        lines = handle.readlines()

    validate_all_urls(lines)
    if args.validate_only:
        sys.exit(0)

    # Write to docs/
    with open(INDEX_MD_PATH, "w") as handle:
        # Add toc limit
        for ln in add_toc_depth_limit():
            print(ln, file=handle)

        # Output index.md file
        for ln in filter_gh_toc(lines):
            print(ln, file=handle, end="")

