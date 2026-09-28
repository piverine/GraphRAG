import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def parse_and_chunk_pdf(
    pdf_path: str,
    chunk_size: int = 12000,
    chunk_overlap: int = 800
) -> List[Document]:
    """
    Parses a research paper PDF and splits it into structured text chunks
    with provenance metadata attached.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
        
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    # Extract filename / arXiv ID for metadata provenance
    filename = os.path.basename(pdf_path)
    paper_id = filename.replace(".pdf", "")
    
    # Attach paper metadata to each page
    for i, page in enumerate(pages):
        page.metadata["paper_id"] = paper_id
        page.metadata["source_file"] = filename
        page.metadata["page_number"] = i + 1

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_documents(pages)
    
    # Attach chunk index for provenance traceability
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{paper_id}_c{idx}"
        
    return chunks

if __name__ == "__main__":
    # Test on Vaswani et al. (Attention Is All You Need)
    test_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "papers", "1706.03762.pdf")
    if os.path.exists(test_pdf):
        print(f"Testing parsing and chunking on: {test_pdf}")
        chunks = parse_and_chunk_pdf(test_pdf)
        print(f"✅ Produced {len(chunks)} chunks from PDF.")
        if chunks:
            print("\nSample Chunk 0 Metadata:", chunks[0].metadata)
            print("Sample Chunk 0 Content Preview (first 200 chars):\n", chunks[0].page_content[:200])
