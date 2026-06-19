# AI Multi-Agent Research Assistant

A distributed multi-agent research pipeline built on AWS. Given a topic, multiple specialized AI agents collaborate to produce a well-researched, fact-checked report.

## Live API

The researcher agent is deployed and live on AWS Lambda + API Gateway:

```bash
curl -X POST https://e1ncymtrq5.execute-api.us-east-1.amazonaws.com/ \
    -H "Content-Type: application/json" \
    -d '{"topic": "your topic here"}'
```

**Architecture:** API Gateway → Lambda → Tavily (web search) → Amazon Bedrock (Claude Haiku 4.5) → structured JSON response

## Architecture

- **Researcher Agent** — searches the web for relevant sources
- **Fact Checker Agent** — validates claims across sources
- **Writer Agent** — produces a structured markdown report
- **Critic Agent** — reviews and scores the report

## Tech Stack

- **Orchestration** — AWS Step Functions
- **Compute** — AWS Lambda
- **LLM** — Amazon Bedrock (Claude)
- **Search** — Tavily Search API
- **API** — Amazon API Gateway
- **Monitoring** — Amazon CloudWatch


## Getting Started

1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `make install`
5. Copy `.env.example` to `.env` and fill in your values
6. Run tests: `make test`

## Environment Variables

See `.env.example` for required environment variables.

## License

MIT
