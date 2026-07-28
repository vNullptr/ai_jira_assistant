#!/bin/bash
echo "Starting Ollama server..."
ollama serve &
sleep 5
echo "Pulling model..."
ollama pull mistral
wait   