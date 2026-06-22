from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Sports Betting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/games")
def get_games():
    return [
        {"id": 1, "home": "Real Madrid", "away": "Barcelona", "odds_home": 2.1, "odds_away": 3.5},
        {"id": 2, "home": "Liverpool", "away": "Man City", "odds_home": 2.8, "odds_away": 2.4},
    ]

@app.post("/bets")
def create_bet(bet: dict):
    return {"message": "Bet created successfully","bet": bet}

@app.get("/bets")
def get_bets():
    return []