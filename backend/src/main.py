from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from pydantic import BaseModel, validator
import os 

class BetRequest(BaseModel):
    game_id: int
    team_chosen: str
    amount: float

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('team_chosen')
    def team_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Team chosen must not be empty')
        return v

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
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unreachable"}
        )
@app.get("/games")
def get_games():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, home_team, away_team, odds_home, odds_away FROM games"))
            games = [{"id": r[0], "home": r[1], "away": r[2], "odds_home": float(r[3]), "odds_away": float(r[4])} for r in result]
        return games
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unreachable")
    

@app.post("/bets")
def place_bet(bet: BetRequest):
    try:
        with engine.connect() as conn:
            # Check game exists
            result = conn.execute(text("SELECT id FROM games WHERE id = :id"), {"id": bet.game_id})
            if not result.fetchone():
                raise HTTPException(status_code=404, detail=f"Game {bet.game_id} not found")
            
            conn.execute(text(
                "INSERT INTO bets (game_id, team_chosen, amount) VALUES (:game_id, :team_chosen, :amount)"
            ), {"game_id": bet.game_id, "team_chosen": bet.team_chosen, "amount": bet.amount})
            conn.commit()
        return {"message": "Bet placed successfully"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/bets")
def get_bets():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, game_id, team_chosen, amount FROM bets"))
            bets = [{"id": r[0], "game_id": r[1], "team_chosen": r[2], "amount": float(r[3])} for r in result]
        return bets
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")
