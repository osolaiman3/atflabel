import bottle from './assets/bottle.png';
import './App.css';
import ProductForm from './components/ProductForm';
import AuthModal from './components/AuthModal';
import React, {useState, useEffect, useCallback} from 'react';
import { API_ENDPOINTS, AUTH_CONFIG } from './config';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState('');
  const [isLoadingAuth, setIsLoadingAuth] = useState(true); // New state for loading authentication status

  // Effect to load token from localStorage on initial mount
  useEffect(() => {
    const cachedToken = localStorage.getItem(AUTH_CONFIG.TOKEN_KEY);
    if (cachedToken) {
      setToken(cachedToken);
    } else {
      setIsLoadingAuth(false); // No token found, so not authenticated, stop loading
    }
  }, []);

  // Callback function to verify the token with the backend
  const verifyToken = useCallback(async () => {
    if (!token) { // If no token exists, we are not authenticated
      setIsAuthenticated(false);
      setIsLoadingAuth(false);
      return;
    }

    try {
      const response = await fetch('/verify-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Send token in Authorization header
        },
        body: JSON.stringify({ token }), // Also send in body if backend expects it
      });
      const data = await response.json();

      if (response.ok && data.valid) {
        setIsAuthenticated(true);
      } else {
        console.error('Token validation failed:', data.message || response.statusText);
        setIsAuthenticated(false);
        localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY); // Remove invalid token
      }
    } catch (error) {
      console.error('Error verifying token:', error);
      setIsAuthenticated(false);
      localStorage.removeItem('token');
    } finally {
      setIsLoadingAuth(false); // Authentication check is complete
    }
  }, [token]); // Dependency on token

  // Effect to run token verification when the token state changes
  useEffect(() => {
    if (token) { // Only verify if a token is present
      verifyToken();
    }
  }, [token, verifyToken]);

  // Effect to save token to localStorage whenever it changes
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  return (
    <div className="App">
      <header className="App-header">
        <div className="flex items-center flex-direction row justify-center space-x-4">
          <p className="text-5xl text-amber-200 font-bold">TTB</p>
          <div>
            <div>
              <img src={bottle} className="App-bottle" alt="bottle" />
            </div>
          </div>
          <p className="text-5xl text-amber-200 font-bold">Scanner</p>
        </div>
        
        

      </header>
      <main>
        
          <h2 className="text-2xl font-semibold mb-4 text-center text-white">
            Alcoholic Beverage Product Verification
          </h2>
          {isLoadingAuth ? (
            <p className="text-2xl font-semibold text-white">Loading authentication...</p>
          ) : isAuthenticated ? (
            <div className="h-4"><ProductForm token={token} /></div>
          ) : (
            <AuthModal onAuthSuccess={(newToken) => {
              setToken(newToken);
              setIsAuthenticated(true); // This will be confirmed by verifyToken
            }} />
          )} 
      </main>
    </div>
  );
}

export default App;
