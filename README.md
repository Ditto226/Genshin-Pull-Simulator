# Genshin Pull Simulator API & CLient

A decoupled, full-stack simulation engine that models genshin gacha mechanics (pity tracking, probability scaling, guarantees) built using an asynchronous architectural pattern.

## 🌟 Key Features
* **Decoupled Architecture:** Clean separation of concerns between an independent FastAPI backend service and a lightweight client CLI.
* **State Persistence:** Custom SQLite layer tracking granular user profiles, pity systems, and queryable pull history logs.
* **Robust Middlewares & Logging:** Incorporates request Interceptors for telemetry and thread-safe rolling file handlers.
* **Dockerized Deployment**: Containerized backend for seamless, zero-config environment setup.

## 🛠 Tech Stack
* **Backend:** Python, FastAPI, Pydantic, SQLite3, Uvicorn, Docker
* **Frontend:** Python Requests CLI 

## Credit
* **Capturing Radiance Implementation** : Modeled based on community research and statistical data. Special thanks to the detailed breakdown found in this Reddit Analysis.

https://www.reddit.com/r/Genshin_Impact/comments/1f3ykny/capturing_radiance_details_observations_and/

## 🚀 Quick Start & Usage

Follow these steps to clone the repository, spin up the backend server, and start simulating pulls.

### 1. Clone the Repository
```bash
git clone https://github.com/Ditto226/Genshin-Pull-Simulator.git
cd Genshin-Pull-Simulator
```

### 2. Run the server
💡 Prerequisite: Make sure Docker Desktop is open and running on your machine.

Launch the containerized FastAPI backend. This handles the database initialization and exposes the simulation APIs.
```bash
docker compose up --build
```

### 3. Run the Application 
Open a new terminal window, navigate to the source directory, and launch the interactive CLI.
```bash
python Codes/client.py
```

### 4. Start Simulating!
Follow the CLI prompts to manage your profile, roll on banners, and track your history. Pity counters and "Capturing Radiance" probability tracking persist automatically in the database.
