"""Download the reference corpus listed in the manifest and verify each file's SHA-256.

Usage: uv run python scripts/download_corpus.py [--manifest PATH] [--dest DIR]
"""

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path, PurePosixPath

from governed_rag.retrieval.corpus import SourceDocument, load_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]
# nvlpubs.nist.gov rejects urllib's default User-Agent with 403.
USER_AGENT = "governed-rag-corpus-downloader/0.1"

try:
    # Use the OS certificate store, so TLS verification also works behind
    # proxies whose root certificate is installed system-wide.
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(doc: SourceDocument, dest: Path) -> Path:
    suffix = PurePosixPath(doc.source_url.path or "").suffix
    target = dest / f"{doc.doc_id}{suffix}"
    if target.exists() and sha256_of(target) == doc.sha256:
        print(f"ok        {target.name} (already present)")
        return target

    partial = target.with_name(target.name + ".part")
    request = urllib.request.Request(str(doc.source_url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        partial.write_bytes(response.read())

    actual = sha256_of(partial)
    if actual != doc.sha256:
        partial.unlink()
        raise ValueError(f"Checksum mismatch for {doc.doc_id}: expected {doc.sha256}, got {actual}")
    partial.replace(target)
    print(f"verified  {target.name}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "data/corpus/manifest.toml")
    parser.add_argument("--dest", type=Path, default=REPO_ROOT / "data/corpus/raw")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    args.dest.mkdir(parents=True, exist_ok=True)

    failures = 0
    for doc in manifest.documents:
        try:
            fetch(doc, args.dest)
        except (OSError, ValueError) as exc:
            print(f"FAILED    {doc.doc_id}: {exc}", file=sys.stderr)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
