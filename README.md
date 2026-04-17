# Eventra-AI

## 1. Title and Description

The orchestration of large-scale engagements—spanning global conferences, specialized music festivals, and highly technical sporting events—represents one of the most complex, multi-stakeholder operational challenges in modern enterprise environments.

Historically, the logistical execution of such events has been plagued by severe data fragmentation, requiring event organizers to manually coordinate across a disparate ecosystem of non-interoperable tools.

Eventra-AI emerges as a comprehensive, open-source solution designed to obliterate these operational silos. Engineered as an end-to-end intelligent conference organizer system, Eventra-AI leverages a sophisticated multi-agent artificial intelligence architecture to automate discovery, decision-making, and execution across the entire event lifecycle.

Rather than starting from a blank slate for every new conference, organizers utilizing Eventra-AI can rely on agents that autonomously scrape, aggregate, and analyze data from events held globally over the past 12 to 24 months.

## 2. Architecture

Eventra-AI uses an **Event-Driven Multi-Agent Architecture**.

### Core Layers

#### 1. Client Interface Layer (React/Vite)
- React 18/19 with Vite
- Real-time dashboards via WebSockets
- Chart.js & Framer Motion integration
- JWT-based authentication (RBAC)

#### 2. Backend (Spring Boot)
- Java 17 + Spring Boot 3
- REST APIs with Swagger
- Handles CRUD + event ingestion

#### 3. Event Streaming Engine
- Apache Kafka for event-driven communication
- Redis for real-time metrics
- TimescaleDB for time-series analytics

#### 4. Multi-Agent Orchestrator
- Built using CAMEL + OpenClaw principles
- Strict input/output schemas
- Centralized + isolated memory model (RAG)

#### 5. Rule Engine
- Drools-based rule evaluation
- Adaptive polling (30s → 100ms)

#### 6. Web3 Execution Layer
- Smart contracts for automated payouts
- Oracle-based verification
- Ethereum-based execution

## 3. Features

### 3.1 Multi-Agent System
- Sponsor Agent
- Speaker Discovery Agent
- Exhibitor Clustering Engine
- Venue Optimization Agent
- Pricing Prediction Agent
- GTM Strategy Agent
- Event Execution Builder

### 3.2 Intelligence Layer
- RAG-based memory
- Real-time data scraping
- Context-aware recommendations

### 3.3 Platform Features
- Admin dashboards
- Hackathon Hub
- Project Gallery
- Feedback system

### 3.4 Analytics
- Live dashboards
- Adaptive alerts
- Real-time metrics tracking

## 4. Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js (v18+)
- Java 17 + Maven
- Python 3.10+
- Hardhat / Foundry (Web3)

### Installation

```bash
git clone https://github.com/YourOrg/Eventra-AI.git
cd Eventra-AI

git submodule update --init --recursive
````

#### Frontend

```bash
cd frontend
yarn install
```

#### Agents

```bash
cd agents_core
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Smart Contracts

```bash
cd contracts
npm install
npx hardhat compile
```

### Configuration (.env)

```env
POSTGRES_URL=jdbc:postgresql://localhost:5432/eventra_ts
REDIS_URL=redis://localhost:6379
KAFKA_BROKERS=localhost:9092

OPENAI_API_KEY=sk-...
LINKEDIN_SCRAPER_TOKEN=...

SEPOLIA_RPC_URL=...
PRIVATE_KEY=...
```

### Run Locally

#### Start Infrastructure

```bash
docker-compose up -d --build
```

#### Backend

```bash
cd backend
./mvnw spring-boot:run
```

#### Agents

```bash
cd agents_core
source venv/bin/activate
python main_orchestrator.py
```

#### Frontend

```bash
cd frontend
yarn dev
```

## 5. Usage

1. Create event (domain, audience, budget)
2. Trigger AI agents
3. Monitor real-time dashboard
4. Review recommendations
5. Confirm → triggers smart contract execution

## 6. Deployment

* Frontend: Vercel
* Backend: Azure / Kubernetes
* Kafka: Confluent Cloud
* CI/CD: GitHub Actions

## 7. Project Status

* Architecture complete
* Smart contracts deployed (Sepolia)
* Dataset ready (2025–2026 events)

## 8. Contributing

Guidelines:

* Maintain strict agent boundaries
* Respect memory architecture
* Write clean, descriptive code

Steps:

1. Fork repo
2. Create branch
3. Submit PR

## 9. License

MIT License
