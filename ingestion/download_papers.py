import os
import time
import urllib.request
import arxiv

PAPERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "papers")

# Target list of impactful papers in the attention / transformer lineage
TARGET_ARXIV_IDS = [
    "1706.03762",  # Attention Is All You Need (Vaswani et al.)
    "1810.04805",  # BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al.)
    "1906.08237",  # XLNet: Generalized Autoregressive Pretraining (Yang et al.)
    "1907.11692",  # RoBERTa: A Robustly Optimized BERT Approach (Liu et al.)
    "1910.13461",  # BART: Denoising Sequence-to-Sequence Pre-training (Lewis et al.)
    "1910.10683",  # T5: Exploring the Limits of Transfer Learning (Raffel et al.)
    "2004.05150",  # Longformer: The Long-Document Transformer (Beltagy et al.)
    "2001.04451",  # Reformer: The Efficient Transformer (Kitaev et al.)
    "2006.04768",  # Linformer: Self-Attention with Linear Complexity (Wang et al.)
    "2009.06732",  # Big Bird: Transformers for Longer Sequences (Zaheer et al.)
    "2005.14165",  # Language Models are Few-Shot Learners (GPT-3, Brown et al.)
    "2104.09864",  # RoFormer: Enhanced Transformer with Rotary Position Embedding (Su et al.)
    "2205.14135",  # FlashAttention: Fast and Memory-Efficient Exact Attention (Dao et al.)
    "2307.08691",  # FlashAttention-2: Faster Attention with Better Parallelism (Dao)
]

def download_file(url: str, dest_path: str):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
        out_file.write(response.read())

def download_corpus():
    os.makedirs(PAPERS_DIR, exist_ok=True)
    print(f"Downloading corpus into: {PAPERS_DIR}")
    client = arxiv.Client()
    
    # 1. Fetch targeted seminal/lineage papers
    search = arxiv.Search(id_list=TARGET_ARXIV_IDS)
    downloaded = 0
    
    for result in client.results(search):
        clean_id = result.get_short_id().split('v')[0]  # base id e.g. 1706.03762
        pdf_filename = f"{clean_id}.pdf"
        target_path = os.path.join(PAPERS_DIR, pdf_filename)
        
        if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
            print(f"Skipping (already exists): {pdf_filename} - {result.title}")
            downloaded += 1
            continue
            
        print(f"Downloading [{downloaded + 1}/{len(TARGET_ARXIV_IDS)}]: {pdf_filename} - {result.title}")
        try:
            download_file(result.pdf_url, target_path)
            downloaded += 1
            time.sleep(0.5)  # polite rate limiting
        except Exception as e:
            print(f"Failed to download {pdf_filename}: {e}")

    # 2. Supplementary search to reach 15-20 papers if needed
    if downloaded < 15:
        print("Fetching supplementary papers to ensure dense subfield coverage...")
        search_query = arxiv.Search(
            query="cat:cs.CL AND (attention OR transformer OR bert)",
            max_results=10,
            sort_by=arxiv.SortCriterion.Relevance
        )
        for result in client.results(search_query):
            if downloaded >= 16:
                break
            clean_id = result.get_short_id().split('v')[0]
            pdf_filename = f"{clean_id}.pdf"
            target_path = os.path.join(PAPERS_DIR, pdf_filename)
            if not os.path.exists(target_path):
                print(f"Downloading search result: {pdf_filename} - {result.title}")
                try:
                    download_file(result.pdf_url, target_path)
                    downloaded += 1
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Failed: {e}")

    existing_files = [f for f in os.listdir(PAPERS_DIR) if f.endswith(".pdf")]
    print(f"\n✅ Corpus acquisition complete! Total PDF papers in {PAPERS_DIR}: {len(existing_files)}")
    for pdf in sorted(existing_files):
        size_mb = os.path.getsize(os.path.join(PAPERS_DIR, pdf)) / (1024 * 1024)
        print(f" - {pdf} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    download_corpus()
