# "BreathGuard AI" Multi-Agent System Using Coral Protocol

This guide provides a step-by-step process to set up, build, and run the complete multi-agent backend for the "BreathGuard AI" project using the latest version of Coral Protocol.

## Introduction

#### What is Coral?
Coral Protocol provides a collaboration infrastructure for AI agents. It allows us to build a system where specialized agents (e.g., Symptom Analyzer, Health Coach) can discover each other, communicate securely, and work together to achieve a common goal—providing real-time COPD patient support.

In this project, we are application developers using Coral Protocol's local mode to build a multi-agent system from a set of custom Python agents, orchestrated by the Coral Server.


## Prerequisites

Before you set up and run Coral, make sure your local environment has the following tools installed.

These are required to run agents, Coral Server, Coral Studio, and external LLMs like OpenAI.

### Check Dependencies

We've provided a convenient script to check all required dependencies:

```bash
./check-dependencies.sh
```

This script will verify that you have all the required tools and versions installed.

### Required Tools & Versions

| Tool | Version | Why You Need It                                             |
|------|---------|-------------------------------------------------------------|
| **Python** | 3.10+ | Needed for the agents in this guide         |
| **uv** | latest | Python environment & dependency manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/)). **Ensure it's installed globally, not as part of a specific python context.** |
| **Node.js** | 18+ | Required to run Coral Studio (the UI)                       |
| **npm** | latest | Bundled with Node.js, used for package management |
| **Git** | latest | For version control and updates                              |
| **Java** | 21+ | Required to run Coral Server                                |
| **API Keys** | Any | You will need keys for Mistral AI, ElevenLabs, etc., as defined in the agent configurations.                 |

### Recommended Tools

| Tool | Reason |
|------|--------|
| **Visual Studio Code** | IDE for editing agent code and config |

---

## Note on Docker
All of these components are possible to run in Docker containers, but for this guide we will be running them locally.

See our Docker guide for more details on how to run Coral in Docker: [Coral Docker Guide](./docker-guide.md)

## Note on Windows
If you're on Windows, you may need to use WSL (Windows Subsystem for Linux) to run the commands in this guide. PowerShell may not work correctly with some of the commands.

WSL 2 works, but WSL1 performs better.

Alternatively, you may use Docker, but Windows users may suffer from performance issues with Docker Desktop since windows forces all containers to run in WSL2.

# Project Setup (V1 Configuration)

This project uses the modern Coral V1 configuration, which is modular and managed through `.toml` files.

### 1. File Structure

```
/backend/
├── coral-server/   (use `git clone https://github.com/Coral-Protocol/coral-server.git`)
│   └── ... (all its files)
│
├── agents/
│   ├── personal_health_coach/  # <-- Agent 3
│   │   ├── main.py             # Your FastAPI/Flask app for this agent
│   │   ├── knowledge/          # Medical docs for your RAG
│   │   ├── run_agent.sh        # Script to start the agent (sets up venv)
│   │   ├── requirements.txt
│   │   └── coral-agent.toml    # <-- V1 AGENT DEFINITION
│   │
│   ├── symptom_analyzer/       # <-- Agent 2
│   │   ├── main.py
│   │   ├── run_agent.sh
│   │   ├── requirements.txt
│   │   └── coral-agent.toml    # <-- V1 AGENT DEFINITION
│   │
│   └── ... (folders for Agent 1, 4, 5)
│
├── registry.toml               # <-- V1 MASTER REGISTRY
├── config.toml                 # <-- V1 Server configuration (optional, for advanced settings)
└── docker-compose.yml          # The master file to run everything
```

### 2. Master Agent Registry (registry.toml)

This file tells the Coral Server where to find the definitions for all our agents. The paths must be the absolute paths inside the Docker container.

```
# backend/registry.toml

[[local-agent]]
path = "/agents/personal_health_coach"

[[local-agent]]
path = "/agents/interface"

[[local-agent]]
path = "/agents/symptom_analyzer"

[[local-agent]]
path = "/agents/exacerbation_predictor"

[[local-agent]]
path = "/agents/critical_alert_manager"

[[local-agent]]
path = "/agents/environment_monitor"
```

### 3. Per-Agent Definition (coral-agent.toml)

Each agent's directory must contain a coral-agent.toml file. This file is the agent's contract—it declares what it's called, what settings it needs, and how to run it.

Example: `agents/personal_health_coach/coral-agent.toml`
```
[agent]
name = "PersonalHealthCoach"
version = "0.1.0"
description = "Provides personalized COPD management advice using a RAG system."

[options.MISTRAL_AI_API_KEY]
type = "string"
description = "API key for the Mistral AI model."

[runtimes.executable]
command = ["bash", "/agents/personal_health_coach/run_agent.sh"]
```

# How to Run the System

### Step 1: Start the Coral Server (in one terminal)
This single command builds and runs the Coral Server inside a Docker container. The server will read your configuration and be ready to spawn agents.

```
# Make sure you are in the 'backend' directory
docker-compose up --build
```

You will see logs from the Coral Server. A successful startup will show lines like:
```
Loaded registry file in X ms
Starting sse server on port 5555
```

#### Step 2: Start Coral Studio (in a NEW terminal)
```
This can be run from any directory
npx @coral-protocol/coral-studio
```
Now, open your web browser and navigate to `http://localhost:5173` or `http://localhost:3000`

You should see:
- A dashboard for Coral Studio
- An option to create a session or connect to Coral Server
- A visual interface to observe and interact with threads and agents

---

## Creating a Session

1. Connect to Server: In Coral Studio, click the server dropdown, select "Add a server," and enter localhost:5555.
2. New Session: Click the session dropdown and select "New session".
3. Pick Agents:
     - Click "New agent" and you will see a dropdown of all the agents you defined in registry.toml (e.g., "PersonalHealthCoach").
     - Select the agents you need for your test.
4. Provide Options: For each agent you add, Coral Studio will automatically create input fields for the options you defined in its coral-agent.toml file (e.g., "MISTRAL_AI_API_KEY"). Paste your secret API keys here.
5. Create a Group: Go to the "Groups" section and create a new group that includes all the agents you've added. This allows them to communicate with each other.
6. Click "Create" to start the session. The Coral Server will now execute the command specified in each agent's configuration, spawning your Python processes.
   
You can now use the "Threads" and "Tools" tabs in Coral Studio to interact with your agents and observe their collaboration.

## Troubleshooting

  - Browser shows 404/Cannot Be Found at localhost:5555: This is normal! The server is an API server, not a website. You must interact with it via Coral Studio (localhost:5173) or your own application.
  - Build Fails or Acts Strange: Run a completely clean build by first stopping everything with docker-compose down, then rebuilding without cache: docker-compose build --no-cache, and finally starting with docker-compose up.