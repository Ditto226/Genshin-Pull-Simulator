# Genshin Pull Simulator API & CLient

A decoupled, full-stack simulation engine that models genshin gacha mechanics (pity tracking, probability scaling, guarantees) built using an asynchronous architectural pattern.

## 🌟 Key Features
* **Decoupled Architecture:** Clean separation of concerns between an independent FastAPI backend service and a lightweight client CLI.
* **State Persistence:** Custom SQLite layer tracking granular user profiles, pity systems, and queryable pull history logs.
* **Robust Middlewares & Logging:** Incorporates request Interceptors for telemetry and thread-safe rolling file handlers.

## 🛠 Tech Stack
* **Backend:** Python, FastAPI, Pydantic, SQLite3, Uvicorn
* **Frontend:** Python Requests CLI (Upgradeable to TUI)

## Credit
* **capturing radiance mechanic** : https://www.reddit.com/r/Genshin_Impact/comments/1f3ykny/capturing_radiance_details_observations_and/

## 🚀 Quick Start & Usage

Follow these steps to clone the repository, spin up the backend server, and start simulating pulls.

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
```

### 2. Install Dependencies
This project relies on a few external libraries. You can install them all in a single command:
```bash
pip install fastapi uvicorn requests pydantic
```

### 3. Run the Application (Requires 2 Terminals)
* **Terminal 1**: Start the Backend Server
Launch the FastAPI server to initialize the SQLite database and handle the core gacha mechanics:
```bash
python server.py
```

* **Terminal 2**: Launch the Client Simulator
Switch to a new terminal window to interact with the CLI:
```bash
python client.py
```

### 4. Start Simulating!
Follow the CLI prompts to manage your profile, roll on banners, and track your history. Pity counters and "Capturing Radiance" probability tracking persist automatically in the database.
