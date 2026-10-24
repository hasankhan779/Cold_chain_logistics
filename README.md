# Cold-Chain Logistics AI Operations Console (FDE)

An enterprise-grade, autonomous AI assistant and monitoring platform for temperature-sensitive cargo logistics. 

Built following **Forward Deployed Engineer (FDE)** production standards:
- Decoupled `src/` architecture
- High-throughput SQL ingestion from legacy CSV telemetry
- Vector RAG over Standard Operating Procedures (SOP v2.4) using local CPU embeddings
- Live weather route checking via Open-Meteo
- LangGraph stateful agent orchestration using Anthropic Claude
- Interactive operations dashboard with Streamlit

---

## 🛠️ Tech Stack & Zero-Cost Architecture

| Component | Technology | Cost Profile |
|---|---|---|
| **Orchestration & Agent** | [LangGraph](https://github.com/langchain-ai/langgraph) + [Anthropic Claude](https://www.anthropic.com/) | Pay-per-use LLM tokens |
| **Relational Database** | [PostgreSQL 18](https://www.postgresql.org/) + SQLAlchemy + psycopg3 | 100% Free / Local |
| **Vector Store (RAG)** | [Pinecone Serverless](https://www.pinecone.io/) | Free Tier Index |
| **Dense Embeddings** | [Hugging Face Sentence-Transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (`all-MiniLM-L6-v2`) | 100% Free / Local CPU |
| **Transit Route Weather** | [Open-Meteo REST API](https://open-meteo.com/) | 100% Free (No API Key needed) |
| **Frontend UI** | [Streamlit](https://streamlit.io/) | 100% Free / Local |

---

## 📂 Project Architecture

```text
Cold_chain_logistics(FDE)/
├── .env                                  # Local environment secrets & DB credentials
├── .env.example                          # Configuration template
├── requirements.txt                      # Pinned Python package dependencies
├── app.py                                # Root Streamlit entrypoint
│
├── data/
│   ├── legacy/
│   │   └── dynamic_supply_chain_logistics_dataset.csv  # Phase 1: 32,065 historical rows
│   └── sops/
│       └── Cold_Chain_Incident_SOP_v2.md               # Phase 2: Domain SOP rulebook
│
├── scripts/                              # Batch Ingestion Pipelines
│   ├── ingest_legacy_to_db.py            # Streamlines CSV -> PostgreSQL (32,065 rows)
│   └── ingest_sops_to_pinecone.py        # Chunks, locally embeds, & upserts SOPs to Pinecone
│
├── src/                                  # Decoupled Application Packages
│   ├── config/settings.py                # Pydantic configuration & env loading
│   ├── db/
│   │   ├── connection.py                 # SQLAlchemy engine & session pool
│   │   ├── models.py                     # 26-column ShipmentTelemetry ORM schema
│   │   └── repository.py                 # Query data access layer & business filters
│   ├── rag/
│   │   ├── embeddings.py                 # Local Hugging Face embedding provider
│   │   └── vector_store.py               # Pinecone query & index wrapper
│   ├── services/
│   │   └── weather_service.py            # Open-Meteo transit corridor weather integration
│   ├── agent/
│   │   ├── state.py                      # LangGraph TypedDict state
│   │   ├── prompts.py                    # FDE domain guardrails & SOP v2.4 instructions
│   │   ├── tools.py                      # DB query, SOP search, and Weather tools
│   │   └── graph.py                      # ReAct agent compilation with Claude
│   └── ui/
│       └── app.py                        # Streamlit dashboard layout & chat interface
│
└── tests/
    └── test_services.py                  # Service integration & sanity checks
```

---

## 🚀 Getting Started

### 1. Ingest Data (One-Time Setup)
```bash
# Phase 1: Ingest 32,065 records into PostgreSQL
python scripts/ingest_legacy_to_db.py

# Phase 2: Embed and upload SOPs into Pinecone
python scripts/ingest_sops_to_pinecone.py
```

### 2. Run the Streamlit Operations Console
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.
