# PETER PAN: Project Execution Plan
**Predictive Agentic Navigator - End-to-End Implementation Roadmap**

**Project Lead:** Reem Mor  
**Timeline:** 4-Week Sprint (July 2026 – August 2026)  
**Objective:** Deliver a production-ready, active AIOps and Incident Response system fulfilling all academic requirements while demonstrating enterprise-grade NOC/SRE engineering capabilities.

---

## 📅 High-Level Timeline
| Phase | Focus Area | Duration | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Infrastructure & Environment Baseline | Days 1-3 | Not Started |
| **Phase 2** | EC2 Microservices Development | Days 4-12 | Not Started |
| **Phase 3** | n8n Orchestration & Active Resolution | Days 13-18 | Not Started |
| **Phase 4** | Enterprise Extensions (Extra Credit) | Days 19-22 | Not Started |
| **Phase 5** | Prompt Engineering & Evaluation Log | Days 23-26 | Not Started |
| **Phase 6** | Final Polish, Demo & Submission | Days 27-28 | Not Started |

---

## 🛠️ Phase 1: Infrastructure & Environment Baseline
**Goal:** Provision cloud infrastructure, set up local development, and initialize baseline repositories.

*   **Task 1.1: AWS EC2 Provisioning**
    *   Launch `t3.large` EC2 instance (Ubuntu).
    *   Configure Security Groups: Restrict inbound TCP ports (8000-8003) to strictly allow n8n IP and local development IP. 
    *   Install Docker and Docker Compose on EC2.
*   **Task 1.2: Development Environment Setup**
    *   Initialize Git repository.
    *   Set up local VS Code / Cursor workspace.
    *   Create `.env` templates for API keys (AWS, Twilio, Slack, Gemini, OpenAI). **Crucial: Add `.env` to `.gitignore`.**
*   **Task 1.3: Initialize n8n & Local LLMs**
    *   Deploy n8n (Cloud or local Docker).
    *   Install Ollama locally and pull `llama3` and `hermes` models.
*   **Deliverable:** Working EC2 instance with Docker running; empty git structure; n8n interface accessible.

---

## 🧠 Phase 2: EC2 Microservices Development
**Goal:** Build, dockerize, and deploy the four core Python FastAPI microservices.

### 2.1 Service 1: RAG Service (Incident Knowledge Base)
*   **Setup:** Initialize FastAPI app.
*   **Implementation:** 
    *   Integrate HuggingFace `sentence-transformers`.
    *   Connect to Supabase pgvector (Managed Vector Store extension).
    *   Implement Llama.cpp for local inference.
*   **Dataset:** Generate ≥30 synthetic NOC incident reports and runbooks (mimicking real-world telco, high-availability gaming/betting, and SaaS architectures).
*   **Acceptance Criteria:** `POST /query` returns top-3 similar incidents and a cited LLM insight. "Not in KB" fallback works.

### 2.2 Service 2: Incident Predictor (PyTorch Time-Series)
*   **Setup:** Synthesize ≥400 labeled metric windows (Category: CPU, Memory, DB Lock, Network; Severity: P5-P1).
*   **Implementation:**
    *   Write the training loop for a 1D-CNN (Transfer Learning).
    *   Train model and export `.pth` checkpoint.
    *   Wrap inference in FastAPI, adding an 85% confidence threshold logic.
*   **Acceptance Criteria:** Model achieves >75% accuracy on the test set. `POST /analyse` returns category, severity, and confidence score.

### 2.3 Service 3: Guardrails Service
*   **Setup:** Initialize NeMo Guardrails.
*   **Implementation:**
    *   Write `topic.co` (Colang) to enforce ops/SRE topics.
    *   Write output rails to block destructive bash commands.
*   **Acceptance Criteria:** `POST /check/input` and `POST /check/output` successfully block malicious payloads and pass clean ones.

### 2.4 Service 4: LangGraph Agent
*   **Setup:** Initialize LangGraph and FastAPI.
*   **Implementation:**
    *   Define Planner, Synthesizer, and Tool nodes.
    *   Connect tool nodes to Service 1 (RAG) and Service 2 (Predictor).
*   **Acceptance Criteria:** `POST /agent/run` successfully coordinates a multi-step triage and returns a structured remediation plan.

### 2.5 Deployment
*   **Task:** Write Dockerfiles for all 4 services. Deploy via `docker-compose up` on EC2. Test endpoints via Postman.

---

## ⚙️ Phase 3: n8n Orchestration & Active Resolution
**Goal:** Wire the e2e incident pipeline and integrate external communication APIs.

*   **Task 3.1: The 8-Node Spine**
    *   Node 1: Webhook Trigger for incoming JSON alerts.
    *   Node 2 & 3: HTTP Request to Guardrails (Input) -> IF Branch.
    *   Node 4: Gemini LM Node (Information Extractor).
    *   Node 5: GPT-4o AI Agent Node (Tool caller pointing to EC2).
    *   Node 6: LLM Chain to format Markdown `TriageReport`.
    *   Node 7: HTTP Request to Guardrails (Output check).
*   **Task 3.2: Active Resolution Routing (Node 8)**
    *   **Slack Integration:** Add Slack API nodes to create `#inc-[service]-[id]` channels, invite on-calls, and pin the `TriageReport`.
    *   **Twilio Integration:** Add logic branch for P1/P2 incidents occurring off-hours to trigger a Twilio TTS voice call.
    *   **HITL (Human-In-The-Loop):** Implement Slack Block Kit interactive buttons for "Approve Fix".
*   **Acceptance Criteria:** An incoming JSON payload automatically traverses the flow and results in a populated Slack channel with correct tool outputs.

---

## 🚀 Phase 4: Enterprise Extensions (Extra Credit)
**Goal:** Implement the four required optional extensions to maximize the project grade.

*   **4.1 Managed Vector Store:** (Completed in 2.1 via Supabase pgvector). Document Precision@3 benchmarks against local ChromaDB.
*   **4.2 Multilingual Guardrail:** Update NeMo input rail to detect and handle Hebrew log snippets seamlessly alongside English.
*   **4.3 Open WebUI & Active Learning:** 
    *   Deploy Open WebUI. Configure local Llama 3 for the SRE Assistant tab.
    *   Create the "Review Queue" logic for outputs with <85% predictor confidence.
*   **4.4 Monitoring Dashboard:** Create a Grafana or Streamlit dashboard plotting n8n execution latency, MTTR, and Guardrail hit rates.

---

## 📝 Phase 5: Prompt Engineering Log
**Goal:** Document the mandatory 5 iterative prompt refinements across 5 surfaces (25% of grade).

*   **Preparation:** Freeze a benchmark set of 10 synthetic incident payloads.
*   **Surface 1 (Extractor):** Iterate n8n extraction prompt for strict JSON adherence.
*   **Surface 2 (Agent Tools):** Iterate tool descriptions in LangGraph/n8n.
*   **Surface 3 (RAG):** Iterate context-injection prompts to eliminate hallucinations and enforce citations.
*   **Surface 4 (Guardrails):** Iterate Colang policies to balance strictness (low false positives).
*   **Surface 5 (Ollama):** Iterate system prompt for the Open WebUI assistant to refuse off-topic real estate/casual queries.
*   **Deliverable:** Compile the `Prompt_Engineering_Log.pdf` documenting V1 through V5 for all surfaces, alongside failure analysis.

---

## 🎬 Phase 6: Final Polish, Demo & Submission
**Goal:** Package the project for final academic evaluation.

*   **Task 6.1: E2E QA Testing**
    *   Run 5 valid incident payloads (clean flow).
    *   Run 2 prompt injection payloads (verify Guardrail blocking).
    *   Test HITL Slack button execution.
*   **Task 6.2: Demo Video Recording**
    *   Record a 5-8 minute walkthrough.
    *   *Script Outline:* 
        1. Inject synthetic alert. 
        2. Show n8n pipeline executing in real-time. 
        3. Show Slack channel creation and Twilio call trigger. 
        4. Demonstrate Open WebUI Ollama chat. 
        5. Show a Guardrail blocking a malicious payload.
*   **Task 6.3: Packaging**
    *   Export n8n workflow JSON.
    *   Ensure all Python services have `requirements.txt` and `Dockerfile`.
    *   Bundle Architecture Markdown, Project Plan, and Prompt Log PDF.
    *   Zip all files into `ReemMor_FinalProject.zip`.

---

## 📊 Definition of Done (DoD) Checklist
- [ ] All 4 EC2 microservices are live and accessible via n8n.
- [ ] PyTorch model `.pth` checkpoint is included in the repository.
- [ ] Active response mechanisms (Slack/Twilio) function correctly.
- [ ] All 4 extra credit extensions are implemented and documented.
- [ ] Prompt Engineering Log contains exactly 25 iterations (5x5) with analysis.
- [ ] Demo video clearly highlights the system's ability to handle realistic NOC events.
