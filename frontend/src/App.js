// frontend/src/App.js

import React, { useState } from 'react';
import './App.css';
import Preconfs from './Preconfs';
import Analytics from './Analytics'; // Assuming you have this component

function App() {
  const [view, setView] = useState('preconfs');

  return (
    <div className="App">
      <header className="App-header">
        <img src="/primev_logo.png" alt="PrimeV Logo" className="logo" />
        <h1> mev-commit Holesky Explorer</h1>
        <nav>
          <button onClick={() => setView('preconfs')}>Preconfs</button>
          <button onClick={() => setView('analytics')}>Analytics</button>
        </nav>
      </header>
      <main>
        {view === 'preconfs' && <Preconfs />}
        {view === 'analytics' && <Analytics />}
      </main>
    </div>
  );
}

export default App;
