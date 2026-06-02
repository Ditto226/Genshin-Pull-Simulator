import os
import json
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status, Request
from pydantic import BaseModel, Field
import uvicorn

from sim_wish import simulate_wish
from calc_stats import calc_stats 

app = FastAPI(title="Gacha Simulator API")

# Server State
banner_json = os.path.join("Data", "banner.json")
banner_data = {}
latest_banner = ""
logger = logging.getLogger("Genshin_Sim_Server")
DB_FILE = os.path.join("Data", "server.db")

def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  
    try:
        yield conn
    finally:
        conn.close()
    # return conn

def init_db():
    """Creates the tables if they don't already exist."""
    os.makedirs("Data", exist_ok=True)
    # with get_db_connection() as conn:
    conn = sqlite3.connect(DB_FILE)
    try:
        # Create Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                pulls INTEGER DEFAULT 0,
                banner_version TEXT,
                pity_5 INTEGER DEFAULT 0,
                pity_4 INTEGER DEFAULT 0,
                guaranteed_5 BOOLEAN DEFAULT 0,
                guaranteed_4 BOOLEAN DEFAULT 0,
                cr_count INTEGER DEFAULT 1
            )
        """)
        # Create Pull Items history table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pull_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                name TEXT NOT NULL,
                rarity INTEGER NOT NULL,
                status TEXT,
                pity INTEGER,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """)
        conn.commit()
    finally:
        conn.close()

# The @app.middleware("http") decorator tells FastAPI to run this for every request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # username = request.headers.get("X-User", "Anonymous")
    # username = request.query_params.get("username", "Anonymous")
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

# --- INITIALIZATION LOGIC ---
def setup_server():
    global banner_data, latest_banner
    
    # 1. Setup Logger
    logger.setLevel(logging.INFO)
    os.makedirs("Data", exist_ok=True)
    handler = RotatingFileHandler("Data/server.log", maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s | %(threadName)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 2. Load Banners
    try:
        with open(banner_json, 'r') as f:
            banner_data = json.load(f)
        latest_banner = list(banner_data.keys())[-1]
    except Exception as e:
        logger.error(f"Failed to load banner data: {e}")
        banner_data = {"default_banner": {"5star": "Standard Character", "4star": ["Weapon A", "Weapon B"]}}
        latest_banner = "default_banner"

    init_db()
    logger.info("[+] Database loaded from disk.")    
    uvicorn.run(app, host="127.0.0.1", port=8000)


# --- DATA MODELS ---
class CustomSetting(BaseModel):
    pity_5: int = Field(default=0, ge=0, le=89)
    pity_4: int = Field(default=0, ge=0, le=9)
    guaranteed_5: bool = False
    guaranteed_4: bool = False
    cr_count: int = Field(default=1, ge=0, le=3)

# --- RESTFUL ROUTES ---
@app.get("/user/{username}")
def get_user(username: str, conn: sqlite3.Connection = Depends(get_db_connection)):
        # 1. Fetch user state
        user_row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user_row:
            return {"status": "success", "exists": True}
        
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/user/{username}/data")
def get_user_data(username: str, conn: sqlite3.Connection = Depends(get_db_connection)):
        # 1. Fetch user state
        user_row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 2. Fetch user pull history items
        item_rows = conn.execute(
            "SELECT name, rarity, status, pity FROM pull_items WHERE username = ?", 
            (username,)
        ).fetchall()

        # Build your payload back to the structure the client expects
        user_dict = dict(user_row)
        user_dict["guaranteed_5"] = bool(user_dict["guaranteed_5"])
        user_dict["guaranteed_4"] = bool(user_dict["guaranteed_4"])
        user_dict["items"] = [dict(item) for item in item_rows]
        
        # Format featured string banner details
        b_info = banner_data.get(user_dict['banner_version'], {"5star": "", "4star": []})
        featured = f"({b_info.get('5star')}) ({', '.join(b_info.get('4star', []))})"
        
        return {"data": user_dict, "featured": featured}
    

@app.post("/user/{username}/data", status_code=201)
def create_account(username: str, request: Optional[CustomSetting] = None, conn: sqlite3.Connection = Depends(get_db_connection)):
    settings = request if request is not None else CustomSetting()
    try:
        conn.execute(
            """INSERT INTO users (username, banner_version, pity_4, pity_5, guaranteed_4, guaranteed_5, cr_count) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (username, latest_banner, settings.pity_4, settings.pity_5, int(settings.guaranteed_4), int(settings.guaranteed_5), settings.cr_count)
        )
        conn.commit()
        b_info = banner_data[latest_banner]
        featured = f"({b_info['5star']}) ({', '.join(b_info['4star'])})"
        return {
            "status": "success", 
            "message": "Account created",
            "user_data": {
                "pulls": 0, "banner_version": latest_banner, "items": [],
                "pity_5": settings.pity_5, "pity_4": settings.pity_4,
                "guaranteed_5": settings.guaranteed_5, "guaranteed_4": settings.guaranteed_4,
                "cr_count": settings.cr_count
            },
            "featured": featured
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")

@app.put("/user/{username}/data")
def reset_account(username: str, request: Optional[CustomSetting] = None, conn: sqlite3.Connection = Depends(get_db_connection)):
    settings = request if request is not None else CustomSetting()
    user_exists = conn.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    conn.execute("DELETE FROM pull_items WHERE username = ?", (username,))

    conn.execute("""
        UPDATE users SET 
            pulls = 0,
            banner_version = ?,
            pity_5 = ?,
            pity_4 = ?,
            guaranteed_5 = ?,
            guaranteed_4 = ?,
            cr_count = ?
        WHERE username = ?
    """, (latest_banner, settings.pity_5, settings.pity_4, int(settings.guaranteed_5), int(settings.guaranteed_4), settings.cr_count, username))

    conn.commit()
    # return {"status": "success", "message": "Account reset"}
    b_info = banner_data[latest_banner]
    featured = f"({b_info['5star']}) ({', '.join(b_info['4star'])})"
    return {
        "status": "success", 
        "message": "Account reset",
        "user_data": {
            "pulls": 0, "banner_version": latest_banner, "items": [],
            "pity_5": settings.pity_5, "pity_4": settings.pity_4,
            "guaranteed_5": bool(settings.guaranteed_5), "guaranteed_4": bool(settings.guaranteed_4),
            "cr_count": settings.cr_count
        },
        "featured": featured
    }

class PullRequest(BaseModel):
    frequency: int

# @app.post("/pull")
@app.post("/user/{username}/pull")
def pull(username:str, request: PullRequest, conn: sqlite3.Connection = Depends(get_db_connection)):
    # 1. Fetch the current state from DB to pass into your simulation engine
    user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
            
    user_state = dict(user_row)
    user_state["guaranteed_5"] = bool(user_state["guaranteed_5"])
    user_state["guaranteed_4"] = bool(user_state["guaranteed_4"])

    # 2. Run your existing simulation logic algorithm
    updated_state = simulate_wish(request.frequency, user_state=user_state)
    
    # 3. Update the user summary record
    conn.execute("""
        UPDATE users SET 
            pulls = ?, pity_5 = ?, pity_4 = ?, 
            guaranteed_5 = ?, guaranteed_4 = ?, cr_count = ?
        WHERE username = ?
    """, (
        updated_state["pulls"], updated_state["pity_5"], updated_state["pity_4"],
        int(updated_state["guaranteed_5"]), int(updated_state["guaranteed_4"]), updated_state["cr_count"],
        username
    ))
    
    # new_items = updated_state["items"][-request.frequency:]
    new_items = updated_state["items"]
    for item in new_items:
        conn.execute("""
            INSERT INTO pull_items (username, name, rarity, status, pity)
            VALUES (?, ?, ?, ?, ?)
        """, (username, item["name"], item["rarity"], item.get("status"), item.get("pity")))
        
    conn.commit()

    full_user_payload = {
        "pulls": updated_state["pulls"],
        "banner_version": user_state["banner_version"],
        "pity_5": updated_state["pity_5"],
        "pity_4": updated_state["pity_4"],
        "guaranteed_5": bool(updated_state["guaranteed_5"]),
        "guaranteed_4": bool(updated_state["guaranteed_4"]),
        "cr_count": updated_state["cr_count"],
    }

    return {
        "status": "success", 
        "data": full_user_payload, 
        "newly_pulled": new_items 
    }

@app.get("/user/{username}/stats")
def get_stats(username: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    # with get_db_connection() as conn:
    user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")

    user_items = conn.execute("SELECT * FROM pull_items WHERE username = ?", (username,)).fetchall()
    return calc_stats(username, user_items)

@app.get("/banner")
def get_banner():
    return {"status": "success", 'banner': banner_data}

class BannerRequest(BaseModel):
    banner_version: str

@app.patch("/user/{username}/data")
def change_banner(username: str, request:BannerRequest, conn: sqlite3.Connection = Depends(get_db_connection)):
    if request.banner_version not in banner_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected banner version does not exist")

    # with get_db_connection() as conn:
    user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    
    conn.execute("UPDATE users SET banner_version = ? WHERE username = ?", (request.banner_version, username))
    conn.commit()
    
    b_info = banner_data[request.banner_version]
    featured = f"({b_info['5star']}) ({', '.join(b_info['4star'])})"
    return {"status": "success", "featured": featured}


if __name__ == "__main__":
    setup_server()
