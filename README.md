# FIXORA

### AI-Assisted Device Troubleshooting Platform

FIXORA is a guided device troubleshooting platform designed to simplify the process of diagnosing and resolving common device issues.

Instead of making users search through lengthy support pages, FIXORA converts a user's problem description into a structured troubleshooting workflow and guides them through actionable steps one at a time.

---

## Problem Statement

Device troubleshooting can often be difficult for users because support information is spread across multiple pages and users may not know which solution to try first.

FIXORA addresses this by providing a structured and guided troubleshooting experience where users can:

* Select their target Galaxy device
* Describe the issue in their own words
* Receive a structured troubleshooting plan
* Follow troubleshooting actions step by step
* Track their progress
* Verify whether an action resolved the issue
* Continue troubleshooting when the issue remains
* Restart the troubleshooting session when required

---

## Key Features

### 1. Natural Problem Description

Users can describe their device problem using everyday language instead of navigating through complicated support menus.

### 2. Guided Troubleshooting

FIXORA converts the reported issue into a structured sequence of troubleshooting actions.

The user is guided through the process one step at a time rather than being presented with an overwhelming list of instructions.

### 3. Progress and Verification

The troubleshooting workflow keeps track of the user's progress and provides verification options so the user can indicate whether the issue has been resolved or continue with the troubleshooting process.

### 4. Device Selection

Users can select the relevant Galaxy device category before beginning the troubleshooting workflow.

### 5. Troubleshooting Session Management

The system maintains the troubleshooting session and provides the ability to restart the workflow when required.

---

## Example Use Case

### Problem

> My phone became very slow after a recent software update.

### Guided Troubleshooting

The system can provide a sequence such as:

1. Restart the device
2. Check available storage
3. Check for additional software updates

The user can then verify whether the problem has been resolved and continue through the troubleshooting workflow if necessary.

---

## System Architecture

FIXORA consists of two primary components:

### Frontend

The frontend provides the user interface for:

* Device selection
* Problem description
* Troubleshooting recommendations
* Step-by-step actions
* Progress tracking
* Verification and session controls

### Backend

The backend provides the API layer responsible for:

* Processing troubleshooting requests
* Creating and managing troubleshooting sessions
* Returning troubleshooting actions
* Tracking session progress
* Handling verification and reset operations

The backend is implemented using **FastAPI**.

---

## Project Structure

```text
FIXORA/
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── ...
│
├── data/
│   └── ...
│
├── README.md
└── ...
```

---

## Running the Project Locally

### Prerequisites

Make sure the following are installed:

* Python
* Node.js
* npm

### Backend Setup

Open a terminal and navigate to the backend:

```bash
cd backend
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Start the backend server:

```bash
uvicorn app:app --reload
```

The backend will run locally on:

```text
http://127.0.0.1:8000
```

### Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local address provided by Vite, typically:

```text
http://localhost:5173
```

Keep both the frontend and backend servers running while using the application locally.

---

## Technology Stack

### Frontend

* React
* Vite
* JavaScript
* HTML/CSS

### Backend

* Python
* FastAPI
* Uvicorn

### Development

* Git
* GitHub
* VS Code

---

## Project Resources

### Presentation

The project presentation is included in this repository.

[fixora ppt final.pdf](https://github.com/user-attachments/files/32864500/fixora.ppt.final.pdf)


### AI Usage Disclosure

The AI usage disclosure submitted for the project is included in this repository.

[LangAI3.0_AI_Disclosure fixora.pdf](https://github.com/user-attachments/files/32864504/LangAI3.0_AI_Disclosure.fixora.pdf)


### Demo Video


https://github.com/user-attachments/assets/5cc5ffb3-5b9d-434a-8d8b-b0a4134299d1



---


## Future Scope

Potential future improvements include:

* Expanding the troubleshooting knowledge base
* Supporting additional device categories
* Adding more troubleshooting scenarios
* Improving personalization of troubleshooting flows
* Integrating additional device diagnostics
* Expanding automated verification capabilities

---

## Team

The team contributed to product design, frontend development, backend development, testing, debugging, documentation, and project presentation.

---

## Hackathon Submission

**Hackathon:** PRISM GenAI Hackathon 2026




## License

This project was developed as a hackathon prototype.
