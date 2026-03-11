# AI Code Review Assistant

An intelligent code review tool that analyzes source code and GitHub repositories to provide automated feedback on code quality, potential issues, and improvements.

## Overview

AI Code Review Assistant helps developers identify potential problems in their code by performing static analysis and generating useful suggestions.

The system can:

* Review pasted Python code
* Analyze GitHub repositories
* Detect common coding issues
* Suggest improvements
* Display structured code review feedback

## Features

* Code quality analysis
* GitHub repository scanning
* Detection of debugging statements
* Detection of TODO comments
* Long line detection
* Unused import detection
* Risk level and quality score generation

## Tech Stack

Backend:

* Python
* FastAPI
* Requests

Frontend:

* HTML
* CSS
* JavaScript

## Project Structure

ai-code-review-assistant/

backend/

* main.py
* reviewer.py
* github_reviewer.py

frontend/

* index.html
* style.css
* script.js

requirements.txt
README.md

## Installation

Clone the repository:

git clone https://github.com/YOUR_USERNAME/ai-code-review-assistant.git

Navigate into the project folder:

cd ai-code-review-assistant

Install dependencies:

pip install -r requirements.txt

Run the backend server:

python -m uvicorn backend.main:app --reload

Open the frontend:

Open frontend/index.html in your browser.

## Usage

### Review Code

1. Paste Python code into the text area
2. Click **Review Code**
3. View suggestions and detected issues

### Review GitHub Repository

1. Enter a GitHub repository URL
2. Click **Review Repository**
3. View code review results for repository files

## Future Improvements

* AI-powered code analysis
* Pull request review integration
* Support for multiple programming languages
* Security vulnerability detection
* Code complexity analysis dashboard

## License

This project is for educational purposes.
