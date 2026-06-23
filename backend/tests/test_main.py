import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app

client = TestClient(app)


# ===================== HEALTH TESTS =====================

def test_health_ok():
    """Health returns 200 when DB is reachable"""
    with patch('src.main.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_down():
    """Health returns 503 when DB is unreachable"""
    with patch('src.main.engine') as mock_engine:
        mock_engine.connect.side_effect = Exception("Connection refused")
        response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "error"


# ===================== GAMES TESTS =====================

def test_get_games_returns_list():
    """GET /games returns a list of games"""
    mock_rows = [
        (1, "Real Madrid", "Barcelona", 2.1, 3.5),
        (2, "Liverpool", "Man City", 2.8, 2.4),
    ]
    with patch('src.main.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_rows
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        response = client.get("/games")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["home"] == "Real Madrid"
    assert data[0]["away"] == "Barcelona"


def test_get_games_db_error():
    """GET /games returns 503 when DB fails"""
    with patch('src.main.engine') as mock_engine:
        mock_engine.connect.side_effect = Exception("DB down")
        response = client.get("/games")
    assert response.status_code == 503


# ===================== BETS TESTS =====================

def test_place_bet_valid():
    """POST /bets with valid data returns 200"""
    with patch('src.main.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = (1,)
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        response = client.post("/bets", json={
            "game_id": 1,
            "team_chosen": "Real Madrid",
            "amount": 50.0
        })
    assert response.status_code == 200
    assert response.json()["message"] == "Bet placed successfully"


def test_place_bet_missing_fields():
    """POST /bets with missing fields returns 422"""
    response = client.post("/bets", json={"game_id": 1})
    assert response.status_code == 422


def test_place_bet_negative_amount():
    """POST /bets with negative amount returns 422"""
    response = client.post("/bets", json={
        "game_id": 1,
        "team_chosen": "Real Madrid",
        "amount": -10.0
    })
    assert response.status_code == 422


def test_place_bet_zero_amount():
    """POST /bets with zero amount returns 422"""
    response = client.post("/bets", json={
        "game_id": 1,
        "team_chosen": "Real Madrid",
        "amount": 0.0
    })
    assert response.status_code == 422


def test_place_bet_empty_team():
    """POST /bets with empty team returns 422"""
    response = client.post("/bets", json={
        "game_id": 1,
        "team_chosen": "   ",
        "amount": 50.0
    })
    assert response.status_code == 422


def test_place_bet_game_not_found():
    """POST /bets with non-existent game_id returns 404"""
    with patch('src.main.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        response = client.post("/bets", json={
            "game_id": 99999,
            "team_chosen": "Real Madrid",
            "amount": 50.0
        })
    assert response.status_code == 404


def test_get_bets_returns_list():
    """GET /bets returns a list"""
    with patch('src.main.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_conn.execute.return_value = []
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        response = client.get("/bets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)