# Phase 2: Document Parsing & Chunking

## Goal
Turn raw PDFs into clean, appropriately-sized text chunks ready for extraction.

## PDF Parsing
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./papers/2301.00001.pdf")
pages = loader.load()  # list of Document objects, one per page
```
Academic PDFs have irregular layouts (two-column text, figures, footnotes). Page-by-page raw text extraction via `pypdf` is sufficient for this project; it will not perfectly handle two-column reflow. This is an acceptable, explicitly-stated simplification — do not attempt full layout-aware parsing unless asked.

## Chunking
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
)
chunks = splitter.split_documents(pages)
```

### Why overlap matters
Without overlap, a sentence describing a relationship ("X, unlike prior work such as Y, achieves...") can be split exactly across two chunks, causing extraction to miss the relationship entirely. 200-character overlap on 1500-character chunks is the starting point; increase if manual review (see `reference/testing-evaluation.md`) shows missed relationships.

### Chunk size trade-offs
| Chunk size | Trade-off |
|---|---|
| Small (~500 chars) | More precise per-chunk extraction, but relationships spanning sentences are more likely split; more LLM calls, higher cost/latency |
| Large (~3000+ chars) | Fewer LLM calls, more context per extraction; but entity/relationship recall tends to degrade as the model tracks more at once |
| Medium (1000-2000 chars) — **recommended default** | Reasonable balance for academic prose, which tends to describe one relationship per few sentences |

## Definition of Done
- [ ] All papers in the corpus parse without error
- [ ] Chunking produces a reasonable number of chunks per paper (typically 15-20 for a standard paper length)
- [ ] Spot-check 2-3 chunks manually to confirm no sentence describing an entity relationship is obviously severed mid-thought
