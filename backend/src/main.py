from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import os 


app = FastAPI(title="Sports Betting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DATABASE connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sportsuser:sportspassword@localhost:5432/sportsdb")
engine = create_engine(DATABASE_URL)

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "database": "unreachable"}
@app.get("/games")
def get_games():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, home_team, away_team, odds_home, odds_away FROM games"))
        games = [{"id": r[0], "home": r[1], "away": r[2], "odds_home": float(r[3]), "odds_away": float(r[4])} for r in result]
    return games

@app.post("/bets")
def place_bet(bet: dict):
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO bets (game_id, team_chosen, amount) VALUES (:game_id, :team_chosen, :amount)"
        ), {"game_id": bet["game_id"], "team_chosen": bet["team_chosen"], "amount": bet["amount"]})
        conn.commit()
    return {"message": "Bet placed successfully"}

@app.get("/bets")
def get_bets():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, game_id, team_chosen, amount FROM bets"))
        bets = [{"id": r[0], "game_id": r[1], "team_chosen": r[2], "amount": float(r[3])} for r in result]
    return bets
