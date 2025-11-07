import { useState } from 'react';
import Dashboard from './components/Dashboard';
import Categories from './components/Categories';
import Bills from './components/Bills';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'categories':
        return <Categories />;
      case 'bills':
        return <Bills />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <div className="navbar">
        <h1>Bill Tracker</h1>
        <nav>
          <button
            className={currentView === 'dashboard' ? 'active' : ''}
            onClick={() => setCurrentView('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={currentView === 'bills' ? 'active' : ''}
            onClick={() => setCurrentView('bills')}
          >
            Bills
          </button>
          <button
            className={currentView === 'categories' ? 'active' : ''}
            onClick={() => setCurrentView('categories')}
          >
            Categories
          </button>
        </nav>
      </div>
      {renderView()}
    </div>
  );
}

export default App;
