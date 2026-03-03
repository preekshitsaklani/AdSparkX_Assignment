import os
import re
import json
import time
import logging
from typing import TypedDict, List, Dict, Any, Optional, Literal
from dotenv import load_dotenv

# langchain wale imports
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# langgraph — the pitch where everything happens
from langgraph.graph import StateGraph, END

# pinecone for vector db — like a library but for AI
from pinecone import Pinecone

# env load karo
load_dotenv()

# logging setup — basic sa
logging.basicConfig(level=logging.INFO)
messi_logger = logging.getLogger("PACSA")  # messi because its the GOAT logger

# ---- CONFIG ----
# tried using a dataclass first but dict is simpler lol
# from dataclasses import dataclass
# @dataclass
# class Config:
#     nvidia_key: str
#     pinecone_key: str
#     ... ye bahut zyada professional lag raha tha

RONALDO_CONFIG = {
    "nvidia_api_key": os.getenv("NVIDIA_API_KEY"),
    "nvidia_model": os.getenv("NVIDIA_MODEL", "z-ai/glm5"),
    "pinecone_api_key": os.getenv("PINECONE_API_KEY"),
    "pinecone_index": os.getenv("PINECONE_INDEX", "adsparkx-assignment"),
    "pinecone_host": os.getenv("PINECONE_HOST"),
    "embed_model": os.getenv("PINECONE_EMBED_MODEL", "llama-text-embed-v2"),
    "embed_dim": 1024,  # llama-text-embed-v2 ka dimension
    "max_retries": 2,  # kitni baar retry kare quality gate fail hone pe
    "quality_threshold": 0.75,  # 75% se upar pass, neeche fail — like a passing mark
    "max_tokens": 16384,
    "temperature": 0.7,
}

# LLM client — the brain of our agent, like the coach
# pehle without extra_body try kiya tha, 504 timeout aa raha tha
# goalkeeper = ChatNVIDIA(model=RONALDO_CONFIG["nvidia_model"], api_key=RONALDO_CONFIG["nvidia_api_key"])
# ^ ye 504 de raha tha
# then enable_thinking=True kiya — worked but BAHUT slow tha, 2-5 min per call
# extra_body={"chat_template_kwargs": {"enable_thinking": True, "clear_thinking": False}},
# ^ slow af, disable kiya ab
goalkeeper = ChatNVIDIA(
    model=RONALDO_CONFIG["nvidia_model"],
    api_key=RONALDO_CONFIG["nvidia_api_key"],
    temperature=RONALDO_CONFIG["temperature"],
    max_tokens=RONALDO_CONFIG["max_tokens"],
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    timeout=120,
)

# Pinecone client — the memory/knowledge base
# tried chromadb first but pinecone is cloud based so better for assignment
# import chromadb
# chroma_client = chromadb.PersistentClient(path="./chroma_db")
# ^ ye local tha, pinecone cloud pe hai

pc = Pinecone(api_key=RONALDO_CONFIG["pinecone_api_key"])
pitch_index = pc.Index(
    RONALDO_CONFIG["pinecone_index"],
    host=RONALDO_CONFIG["pinecone_host"]
)

print("✅ Config loaded | LLM ready | Pinecone connected")
print(f"   Model: {RONALDO_CONFIG['nvidia_model']}")
print(f"   Index: {RONALDO_CONFIG['pinecone_index']}")
