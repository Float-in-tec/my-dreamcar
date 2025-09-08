#!/usr/bin/env bash
docker-compose up -d --build
sleep 4
docker-compose exec dev python -m app.cli_agent
