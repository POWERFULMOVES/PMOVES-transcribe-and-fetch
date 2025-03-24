### **🔥 AI Reasoning System Database Schema & Implementation Plan**  

#### **📌 Overview**
This document outlines the database schema and implementation plan for integrating **CAG-KAG + GraphRAG + Master MCTS** into the `always-on-ai-assistant` project, using **Supabase for self-hosted storage**.

---

## **1️⃣ Database Schema Design**
The system will store AI interactions across **five key tables**:

| Table Name           | Purpose |
|----------------------|---------|
| `user_sessions`      | Tracks user sessions & metadata |
| `messages`          | Stores chat interactions between user & AI |
| `retrieval_logs`    | Logs knowledge retrieval from CAG-KAG & GraphRAG |
| `agent_interactions`| Tracks multi-agent reasoning with Master MCTS |
| `fact_checks`       | Stores AI fact verification results |

---

### **📌 1. `user_sessions` Table**
**Tracks active AI assistant sessions.**  

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users (id) ON DELETE SET NULL,
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP NULL,
    metadata JSONB
);
```

👉 **Key Features:**  
- Links interactions to a **session**  
- Stores **metadata** (device, model version, etc.)  
- Allows **session expiration & archival**  

---

### **📌 2. `messages` Table**
**Stores chat interactions between user and AI.**  

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES user_sessions (id) ON DELETE CASCADE,
    sender TEXT CHECK (sender IN ('user', 'assistant', 'agent')),
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    agent_id UUID REFERENCES agent_interactions (id) ON DELETE SET NULL,
    retrieval_id UUID REFERENCES retrieval_logs (id) ON DELETE SET NULL
);
```

👉 **Key Features:**  
- Saves **messages from user, AI, and agents**  
- Links each message to **retrieval logs & agent activities**  

---

### **📌 3. `retrieval_logs` Table**
**Logs knowledge retrieved via GraphRAG and CAG-KAG hybrid methods.**  

```sql
CREATE TABLE retrieval_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES user_sessions (id) ON DELETE CASCADE,
    retrieval_type TEXT CHECK (retrieval_type IN ('GraphRAG', 'CAG-KAG', 'Hybrid')),
    retrieved_text TEXT NOT NULL,
    retrieval_timestamp TIMESTAMP DEFAULT NOW(),
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    source_metadata JSONB
);
```

👉 **Key Features:**  
- Logs **retrieval type** (GraphRAG, CAG-KAG, Hybrid)  
- Stores **retrieved knowledge & confidence scores**  
- Tracks **retrieval performance**  

---

### **📌 4. `agent_interactions` Table**
**Tracks multi-agent system activities from Master MCTS.**  

```sql
CREATE TABLE agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES user_sessions (id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL,
    task_description TEXT NOT NULL,
    execution_time FLOAT,
    parent_agent_id UUID REFERENCES agent_interactions (id) ON DELETE SET NULL,
    agent_score FLOAT CHECK (agent_score BETWEEN 0 AND 1),
    output TEXT
);
```

👉 **Key Features:**  
- Tracks **AI agent tasks & reasoning process**  
- Links **child agents to parent agents**  
- Stores **execution time & confidence scores**  

---

### **📌 5. `fact_checks` Table**
**Logs AI self-evaluation & fact verification results.**  

```sql
CREATE TABLE fact_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES user_sessions (id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages (id) ON DELETE CASCADE,
    fact_validity BOOLEAN,
    validation_source TEXT,
    llm_confidence FLOAT CHECK (llm_confidence BETWEEN 0 AND 1),
    verification_timestamp TIMESTAMP DEFAULT NOW()
);
```

👉 **Key Features:**  
- **Logs fact-checking results** from AI self-evaluation  
- Stores **confidence scores & external validation sources**  
- Helps **reduce AI hallucinations**  

---

## **2️⃣ Supabase Integration with Python**

### **📌 Install Supabase Client**
```bash
pip install supabase
```

### **📌 Connect to Supabase**
```python
from supabase import create_client, Client

SUPABASE_URL = "https://your-supabase-url.supabase.co"
SUPABASE_KEY = "your-supabase-key"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
```

### **📌 Insert a New Message**
```python
def store_message(session_id, sender, message, agent_id=None, retrieval_id=None):
    data = {
        "session_id": session_id,
        "sender": sender,
        "message": message,
        "agent_id": agent_id,
        "retrieval_id": retrieval_id,
    }
    response = supabase.table("messages").insert(data).execute()
    return response
```

### **📌 Retrieve Conversation History**
```python
def get_messages(session_id):
    response = supabase.table("messages").select("*").eq("session_id", session_id).execute()
    return response.data
```

---

## **3️⃣ Next Steps**
✅ **Revoke & regenerate Supabase keys immediately** 🔥  
✅ **Create these tables in Supabase (`psql` or Supabase UI)**  
✅ **Modify `retriever.py` and `agent_manager.py` to use this database**  
✅ **Test retrieval, message logging, and agent tracking**  

🚀 **This plan ensures secure, structured, and efficient AI reasoning storage in Supabase!** 🚀

