import React from 'react';
import ChatWindow from './Components/ChatWindow.jsx';
import './App.css';
import './colors.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <img src="/logo192.png" alt="Logo" className="logo" />
        <span className="org-name">Example Org</span>
      </header>
      <ChatWindow />
    </div>
  );
}

export default App;
