# Python HTTP Server (Learning Project)

A minimal HTTP server written from scratch in Python to understand how HTTP works at the socket and protocol level.
This project intentionally avoids frameworks and focuses on correctness, simplicity, and learning.

## Features
- TCP socket–based HTTP server
- HTTP/1.0 responses (accepts HTTP/1.0 and HTTP/1.1 requests)
- Static file serving from a document root
- Safe path parsing (no directory traversal)
- Top-level files only (no subdirectories)
- Basic Content-Type handling
- Graceful error responses (400, 404, 501, 505)

## Project Structure
server/
    __init__.py
    main.py        # Server loop and socket handling
    parser.py      # HTTP request parsing & validation
    reader.py      # File reading utilities
    mime_types.py  # Extension → Content-Type mapping

www/               # Document root (static files)
venv/              # Virtual environment (not committed)

## Running the Server
Run the server as a package module (recommended):

python -m server.main

The server listens on:
- 127.0.0.1:8080

Then open a browser and visit:
http://localhost:8080/
