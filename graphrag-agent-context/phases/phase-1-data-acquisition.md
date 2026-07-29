# Phase 1: Data Acquisition from arXiv

## Goal
Build a real, topically coherent corpus of papers. Do not test this system on 3-4 unrelated hand-picked papers — the lineage-tracing and contradiction-finding features only produce interesting results when the papers actually reference and build on each other.

## Using the arXiv API
```python
import arxiv

search = arxiv.Search(
    query="attention mechanism transformer",
    max_results=25,
    sort_by=arxiv.SortCriterion.Relevance,
)

for result in search.results():
    result.download_pdf(dirpath="./papers", filename=f"{result.get_short_id()}.pdf")
```

## Corpus Selection Rules
- Choose **one coherent subfield** (e.g. "attention mechanisms," "graph neural networks," "contrastive learning") — not a scattershot mix of unrelated topics.
- **15–30 papers minimum**, so lineage chains and contradictions have material to actually appear in.
- Deliberately include a few papers known to **cite or critique each other**, to guarantee real examples for `IMPROVES` and `CONTRADICTS` relationships rather than hoping the LLM finds some by chance.

## Common Failure Mode
A sparse, disconnected graph is the single most common reason a GraphRAG demo looks unimpressive. This is a **data curation problem**, not a code problem. Solve it here, before writing any extraction code.

## Definition of Done
- [ ] 15-30 PDFs downloaded into `./papers`, all from one coherent subfield
- [ ] At least 3-4 papers in the set are known (by title/citation) to reference or critique each other
- [ ] File names are consistent and traceable back to arXiv IDs for later provenance linking
