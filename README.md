# 🤖 News Agent

## 1. Introduction

The **News Agent** is a stateful, streaming LLM orchestration system designed to perform iterative research and information synthesis. It combines structured tool usage, graph-based execution, and multi-model reasoning to deliver context-aware responses.

Unlike simple chatbot implementations, this system separates:
- **Reasoning (LLM layer)**
- **Execution (MCP tool server)**
- **Control & state management (this agent)**

---

## 2. Core Capabilities

- Multi-step reasoning with dynamic tool usage  
- Iterative research (fetch → expand → refine)  
- Streaming responses at node-level granularity  
- Stateful conversations with thread tracking  
- Multi-model orchestration for efficiency and cost control  

---

## 3. Architecture Overview

The agent is built using a **graph-based execution model** powered by StateGraph, where each node represents a distinct stage in the reasoning pipeline.

### High-Level Flow

```
User Query → Decision → Keyword Extraction → Tool Invocation → Tool Summarization → LLM Response → Streaming Output
```

---

## 4. Key Components

### 4.1 Execution Engine

- Built using **StateGraph**
- All nodes are **asynchronous**
- Execution is modular and extensible
- Each node contributes to shared state

---

### 4.2 LLM Strategy

Two models are used for optimized performance:

- **GPT-5**
  - Primary reasoning and response generation

- **GPT-5-nano**
  - Lightweight tasks:
    - Summarization  
    - Keyword extraction  
    - Intermediate transformations  

This reduces cost and latency while preserving output quality.

---

### 4.3 Streaming Layer

- Implemented using **FastAPI `StreamingResponse`**
- Streams outputs from **individual nodes**, not just final response
- Provides real-time visibility into:
  - Decision steps  
  - Tool execution  
  - Intermediate summaries  

---

## 5. Execution Graph (Nodes)

The system consists of the following nodes:

### 5.1 Data Fetch Decision Node
- Determines whether external data retrieval is required
- Controls tool invocation flow

---

### 5.2 Keyword Extraction Node
- Breaks down user query into smaller, targeted keywords
- Improves search precision for downstream tools

---

### 5.3 Tools Node
- Invokes MCP server tools via `MultiServerMCPClient`
- Supports:
  - News retrieval  
  - Website scraping  

---

### 5.4 Tool Output Summarization Node
- Processes raw tool outputs
- Converts them into structured, LLM-friendly summaries
- Improves downstream reasoning efficiency

---

### 5.5 Chat Summarization Node
- Maintains concise conversation history
- Prevents context explosion
- Supports long-running sessions

---

### 5.6 LLM Node
- Core reasoning and response generation
- Uses GPT-5
- Produces final output

---

## 6. MCP Integration

The agent integrates with an external MCP server using:

- **MultiServerMCPClient**

### Available Capabilities

- `get_latest_news` → structured news discovery  
- `scrape_website` → markdown-based content extraction  

### Design Principle

- Agent handles **when and why to use tools**
- MCP server handles **execution**

---

## 7. State Management

The system maintains state across execution and sessions using:

- **PostgreSQL database**

### Responsibilities

- Track user IDs and thread IDs  
- Store conversation state  
- Enable continuity across interactions  

---

## 8. Guided Exploration

This enables:
- Deep exploration of topics from suggestions given
- Multi-source synthesis  
- Context-aware reasoning  

---

## 9. Streaming Behavior

Each node emits intermediate outputs which are streamed via FastAPI:

- Decision outputs  
- Tool invocation logs  
- Summarized content  
- Final response  

This provides:
- Transparency  
- Better UX  
- Debuggability  

---

## 10. Design Philosophy

- **Separation of Concerns**
  - Agent → reasoning & control  
  - MCP → execution  
  - Gateway → safety & governance  

- **Graph-Based Execution**
  - Modular and extensible pipeline  

- **Efficiency First**
  - Multi-model usage for cost optimization  

- **LLM-Centric Design**
  - Outputs optimized for downstream reasoning  

---

## 11. Limitations

- No built-in safety controls (handled by gateway layer)  
- No strict recursion limits within agent  
- Tool dependency on external MCP server availability  

---

## 12. Security & Access Model

This service is **not designed for direct public access** and is intended to operate behind a secure gateway layer.

### CORS Policy

CORS is **not enabled** in this FastAPI service.

### Rationale

- The agent is not meant to be consumed directly from browser-based clients  
- All external interactions are expected to go through an upstream **gateway layer**  
- The gateway is responsible for:
  - Authentication  
  - Authorization  
  - Rate limiting  
  - Request validation  
  - CORS handling  

### Architecture Enforcement

```
Client (Browser/UI) → Gateway → Agent → MCP Server
```

This ensures:
- Reduced attack surface  
- Centralized security controls  
- Cleaner separation of concerns  

### Development Note

If direct browser access is required for local development or testing, CORS can be temporarily enabled. However, it is **intentionally excluded in the default setup** to maintain architectural integrity.

---

## 13. Input & Output Contract

### Request Format

The agent is exposed via a streaming HTTP endpoint using FastAPI.

**Request Body (example):**

```json
{
  "user_id": "user_123",
  "thread_id": "thread_456",
  "query": "Explain latest developments in AI regulation"
}
```

### Fields
- `user_id` ‒  Unique identifier for the user
- `thread_id` ‒ Identifier for maintaining conversation continuity
- `query` ‒ User input / question

### Response Format (Streaming)

The agent responds using a streaming interface, where each chunk represents intermediate execution updates.

#### Example Stream Events:
```json
{"type":"node","node_name":"data_fetch_decision_node","node_output":"Determining if external data is required..."}
{"type":"node","node_name":"keyword_extraction_node","node_output":"AI regulation, policy updates, global AI laws"}
{"type":"node","node_name":"tool_output_summarize_node","node_output":"Summarized key articles..."}
{"type":"node","node_name":"llm_node","node_output":"Recent developments in AI regulation include..."}
{"type":"done"}
```
### Design Considerations
- Streaming-first design
  - Enables real-time feedback and transparency
- Node-level granularity
  - Each step in the reasoning pipeline is exposed
- State-aware responses
  - Outputs are influenced by prior conversation stored in PostgreSQL
- LLM-friendly structure
  - Outputs are simple and directly consumable without strict schema enforcement

---

## 14. Environment Configuration

The agent requires the following environment variables to be set before running.

### Required Variables

```bash
# OpenAI / LLM Configuration
OPENAI_API_KEY=your_api_key

# Database Configuration (PostgreSQL)
POSTGRES_CHECKPOINTER_URI=postgresql://admin:admin@news-agent-postgres:5432/newsagent

# MCP Server Configuration
MCP_URI=http://localhost:8000/mcp
```

### Description

- **OPENAI_API_KEY**  
  Used for accessing GPT-5 and GPT-5-nano models

- **POSTGRES_CHECKPOINTER_URI**  
  Used for managing:
  - User sessions  
  - Thread IDs  
  - Conversation state  

- **MCP_URI**  
  Endpoint of the MCP server used for tool execution

---

## 15. Future Enhancements

- Adaptive tool selection strategies  
- Reinforcement-based decision optimization  
- Structured output enforcement  
- Observability (tracing, metrics, logging)  
- Dynamic graph execution (runtime node injection)  

---

## Final Note

This agent is designed as a **control and intelligence layer** in a modular LLM system. Its strength lies in:

- Structured orchestration of reasoning and tools  
- Real-time streaming execution  
- Support for iterative, multi-step research workflows  

It is best deployed alongside:
- A capability-focused MCP server  
- A gateway layer for safety and governance  

---

## 👤 Maintainer
Tuhin Kumar Dutta

- 🌐 Website: https://www.tuhindutta.com/
- 💼 LinkedIn: https://www.linkedin.com/in/t-k-dutta

---

## ⭐ Contribute
Pull requests and issues are welcome.
```bash
git clone https://github.com/tuhindutta/news-agent.git
```
