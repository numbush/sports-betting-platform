
-- Schema init — runs via docker-entrypoint-initdb.d on first Postgres boot only
\c sportsdb;
-- Create tables


CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    odds_home DECIMAL(4,2) NOT NULL,
    odds_away DECIMAL(4,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    team_chosen VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);