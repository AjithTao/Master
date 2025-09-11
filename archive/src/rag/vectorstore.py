from __future__ import annotations
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def build_or_load_vs(text_items: List[Dict[str, str]], persist_dir: str, embeddings_model: str):
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model)
    os.makedirs(persist_dir, exist_ok=True)
    if text_items:
        # build new index from items
        docs = []
        from langchain.docstore.document import Document
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
        for item in text_items:
            for chunk in splitter.split_text(item["text"]):
                docs.append(Document(page_content=chunk, metadata={"title": item.get("title",""), "url": item.get("url","")}))
        vs = FAISS.from_documents(docs, embeddings)
        vs.save_local(persist_dir)
        return vs
    else:
        # load if exists
        return FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)
