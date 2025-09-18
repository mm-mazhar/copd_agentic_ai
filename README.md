
# COPD Agentic AI - Multi-Agent System Using Coral Protocol

### Project Structure

```
COPD-Agentic-AI/
├── .git/               <-- YOUR PROJECT'S MAIN HISTORY
|
|
├── frontend/
│   ├── .next/
│   ├── public/
│   ├── src/
│   ├── next.config.ts
│   ├── package.json
│   └── ... (rest of your Next.js files)
|
├── backend/
|    ├── coral-server/   (use `git clone https://github.com/Coral-Protocol/|coral-server.git`)
|    │   └── ... (all its files)
|    │
|    ├── agents/
|    │   ├── personal_health_coach/  # <-- Agent 3
|    │   │   ├── main.py             # Your FastAPI/Flask app for this agent
|    │   │   ├── knowledge/          # Medical docs for your RAG
|    │   │   ├── run_agent.sh        # Script to start the agent (sets up venv)
|    │   │   ├── requirements.txt
|    │   │   └── coral-agent.toml    # <-- V1 AGENT DEFINITION
|    │   │
|    │   ├── symptom_analyzer/       # <-- Agent 2
|    │   │   ├── main.py
|    │   │   ├── run_agent.sh
|    │   │   ├── requirements.txt
|    │   │   └── coral-agent.toml    # <-- V1 AGENT DEFINITION
|    │   │
|    │   └── ... (folders for Agent 1, 4, 5)
|    │
|    ├── registry.toml               # <-- V1 MASTER REGISTRY
|    ├── config.toml                 # <-- V1 Server configuration (optional, for advanced settings)
|
|    └── docker-compose.yml          # The master file to run everything
|
└── README.md
└── .gitignore
└── .env
```
