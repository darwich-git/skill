import os
import sys
import argparse
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_chroma_path(ticker_dir):
    return os.path.join(ticker_dir, ".chromadb_index")

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_index(ticker_dir):
    print(f"Building index for {ticker_dir}...")
    if not os.path.exists(ticker_dir):
        print(f"Error: Directory {ticker_dir} does not exist.")
        sys.exit(1)
        
    chroma_path = get_chroma_path(ticker_dir)
    
    loader = PyPDFDirectoryLoader(ticker_dir, glob="**/*.pdf")
    documents = loader.load()
    
    if not documents:
        print(f"No PDFs found in {ticker_dir}.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    print(f"Found {len(documents)} PDF pages, split into {len(docs)} chunks.")
    
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=chroma_path)
    vectorstore.persist()
    print("Index built successfully.")

def query_index(ticker_dir, query):
    chroma_path = get_chroma_path(ticker_dir)
    if not os.path.exists(chroma_path):
        print("Error: Index not found. Please build it first.")
        sys.exit(1)
        
    embeddings = get_embeddings()
    vectorstore = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    
    results = vectorstore.similarity_search(query, k=3)
    
    if not results:
        print("No information found.")
        return
        
    print(f"--- RESULTS FOR QUERY: '{query}' ---")
    for i, doc in enumerate(results):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', 'Unknown')
        print(f"\n[Source: {source}, Page: {page}]")
        print(doc.page_content)

def main():
    parser = argparse.ArgumentParser(description="Local RAG for Checklist Skill")
    parser.add_argument("action", choices=["build", "query"], help="Action to perform")
    parser.add_argument("ticker_dir", help="Absolute path to the ticker directory containing PDFs")
    parser.add_argument("--q", dest="query", help="Query string (required if action is 'query')")
    
    args = parser.parse_args()
    
    if args.action == "build":
        build_index(args.ticker_dir)
    elif args.action == "query":
        if not args.query:
            print("Error: --q argument is required for query action.")
            sys.exit(1)
        query_index(args.ticker_dir, args.query)

if __name__ == "__main__":
    main()
