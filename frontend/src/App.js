import React, { useEffect, useState } from 'react';

function App() {
  const [games, setGames] = useState([]);
  const [health, setHealth] = useState('checking...');

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(() => setHealth('error'));

    fetch('/api/games')
      .then(res => res.json())
      .then(data => setGames(data))
      .catch(() => setGames([]));
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Sports Betting Platform</h1>
      <p>API Status: <strong>{health}</strong></p>
      <h2>Games</h2>
      {games.map(game => (
        <div key={game.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
          <strong>{game.home} vs {game.away}</strong>
          <p>Home odds: {game.odds_home} | Away odds: {game.odds_away}</p>
        </div>
      ))}
    </div>
  );
}

export default App;