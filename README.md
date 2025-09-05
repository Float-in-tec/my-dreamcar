# my-dreamcar
Chat agent helps you find the best car for you

(MCP + Gemini)

This project delivers a terminal-based “virtual agent” that interacts with user to find cars in the database.
It uses a minimal MCP server for search and a lightweight LLM step (Gemini) only to extract filters from user responses and to decides if more questions will be asked or if user wants to run query or if user wants to stop conversation.
The goal is to keep the code straight to the point, readable, and close to real-world ready-solution (import/apply solutions, not reinvent).

## Setup

Tested on: Docker 27.5.1 and Docker Compose v2.22.0

- Clone this repo into your machine
- Copy the environment template and set your key:
   ```cp .env.example .env```
   edit .env and set: GEMINI_API_KEY=...  
- Build application:
   ```docker-compose up --build -d```
- Start agent:
  ```docker-compose exec dev bash```
  On container's terminal:
  ```python -m app.cli_agent```

## Environment Variables

- GEMINI_API_KEY     # required by the terminal agent (keep it OUT of version control)
- db-related: hardcoded for testing purposes (no real data/security issue). In real-case scenario, set credentials in .env file (as exampled in env.example)

## Examples (free-form conversation).
Be ware: unrealistis data seeded with few examples (n=100) as requested by the challenge. Results may be lacking or unrealistic (car model that doesn't have electric battery being show as electric).

- I want a new Honda
- I want an electric car with mileage smaller then 90k
- Any brand, flex and automatic

### Seed Data (challenge step)

The DB is auto-seeded so the demo works right away.

### How to obtain a free Gemini API key (easy and quick)

1) Open Google AI Studio in your browser: https://aistudio.google.com/app/apikey
2) Click “Get API key” and follow the prompts to create a key in your Google account.
3) Copy the key and addo to your .env

## Troubleshooting

• “Requires environment variable GEMINI_API_KEY.” — add to your .env or set in container's terminal.
• No results — try a broader query (agent will also relax filters automatically and show similar results).


Notes for reviewers

• The code mirrors reference-style code and vendor glue to avoid “AI-generated code”, and to respect guidelines of using ready solution without the need of unnecessary and complex code.
• All query filters are optional; output fields (as specified by challenge): brand, model, year, color, mileage, price.
