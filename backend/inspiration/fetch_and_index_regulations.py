import os, json, argparse, asyncio, sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List

# Ensure project root is on sys.path when run directly (e.g., python scripts/..)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Reuse existing infrastructure
from backend.infrastructure.ai.scraper import scrape_pages
from backend.infrastructure.ai.rag_service import upsert_documents, get_chroma_client
from backend.applications.use_cases.get_compliance_rules import get_compliance_rules_from_vector_store


DEFAULT_URLS: List[str] = [
    # DGCA FDTL primary (update with exact PDF URL when available)
    "https://www.dgca.gov.in/digigov-portal/?page=2067/4310/list-of-advisories-circulars",
    # Cabin crew FDTL older doc and QRG references (background)
    "https://understandingdgacfdtl2012.files.wordpress.com/2012/09/car-7-j-part-iii.pdf",
    "https://understandingdgacfdtl2012.files.wordpress.com/2012/09/cabin-crew-qrg-fdtl.pdf",
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch DGCA resources, index to vector DB, and export structured rules.")
    parser.add_argument("--url", action="append", help="One or more URLs to scrape (can repeat)")
    parser.add_argument("--urls", help="Path to a JSON file containing an array of URLs")
    parser.add_argument("--out", default=os.path.join("data", "regulations"), help="Output directory for raw and json exports")
    parser.add_argument("--collection", default="compliance_rules", help="Chroma collection name")
    args = parser.parse_args()

    urls: List[str] = []
    if args.urls:
        with open(args.urls, "r", encoding="utf-8") as f:
            urls = list(json.load(f))
    if args.url:
        urls.extend(args.url)
    if not urls:
        urls = DEFAULT_URLS

    out_dir = args.out
    raw_dir = os.path.join(out_dir, "raw")
    ensure_dir(raw_dir)

    print(f"[fetch] Fetching {len(urls)} sources...")
    docs = await scrape_pages(urls)
    print(f"[fetch] Retrieved {len(docs)} documents with text")

    # Save raw text snapshots for auditability
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = []
    for doc in docs:
        source = doc.get("source", "unknown")
        doc_id = doc.get("id", "doc")
        safe_name = doc_id.replace("/", "_")
        out_path = os.path.join(raw_dir, f"{safe_name}-{timestamp}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(doc.get("text", ""))
        manifest.append({"id": doc_id, "source": source, "path": out_path})

    with open(os.path.join(out_dir, f"manifest-{timestamp}.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[index] Upserting chunks to Chroma collection '{args.collection}'...")
    upsert_documents(
        collection_name=args.collection,
        documents=docs,
        metadata={"category": "compliance", "source_type": "web", "ingested_at": timestamp},
        persist_directory=os.getenv("CHROMA_DIR", os.path.join("data", "chroma")),
        chunk_tokens=700,
        chunk_overlap=80,
    )

    # Optional: produce structured, machine-readable rules JSON using the existing RAG extraction
    print("[extract] Generating structured rules (JSON) via RAG extractor...")
    rules = []
    try:
        rules = get_compliance_rules_from_vector_store(top_k=10)
    except Exception as e:
        print(f"[warn] Rule extraction failed: {e}. Writing empty rules list; vectors are indexed.")
    rules_path = os.path.join(out_dir, f"rules-{timestamp}.json")
    with open(rules_path, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)
    # Also update a stable pointer
    with open(os.path.join(out_dir, "rules.latest.json"), "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

    print(f"[done] Indexed {len(docs)} documents. Extracted {len(rules)} rules -> {rules_path}")


if __name__ == "__main__":
    asyncio.run(main())


