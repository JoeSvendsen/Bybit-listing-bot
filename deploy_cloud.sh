#!/bin/bash
# Example deploy script — replace with your provider (Heroku, AWS, GCP, etc.)
echo "Building Docker image..."
docker build -t bybit-notify-bot .
echo "Run with:"
echo "  docker run --env-file .env -v $(pwd)/symbols.db:/app/symbols.db bybit-notify-bot"
