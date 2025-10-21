import React, { useState } from 'react';

// === AuthModal Component (Uses Flask Login at :5000) ===
const AuthModal = ({ onAuthSuccess }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [authFeedback, setAuthFeedback] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:10000';
    const LOGIN_ENDPOINT = `${API_BASE}/login`;

    const handleAuthSubmit = async (e) => {
        e.preventDefault();
        setAuthFeedback('');

        if (username.trim() === '' || password.trim() === '') {
            setAuthFeedback('Username and password cannot be empty.');
            return;
        }

        setIsLoading(true);
        try {
            const res = await fetch(LOGIN_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Authorization': 'Basic ' + btoa(`${username}:${password}`),
                    'Content-Type': 'application/json', // Still include for consistency, though Basic Auth doesn't strictly need it for credentials
                },
                // No need for body: JSON.stringify({ username, password }) for Basic Auth
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                const msg = data.message || data.error || `Login failed (${res.status}).`;
                setAuthFeedback(msg);
                return;
            }

            const token = data.token || data.access_token;
            if (!token) {
                setAuthFeedback('Login succeeded but no token was returned.');
                return;
            }

            localStorage.setItem('token', token);
            onAuthSuccess(token, username);
        } catch (error) {
            setAuthFeedback('Network Error: Failed to connect to backend.');
            console.error('Login error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const inputClass = "w-full p-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-500 focus:ring-amber-500 focus:border-amber-500 transition duration-150";
    const buttonClass = "w-full py-3 bg-amber-500 text-gray-900 font-bold rounded-lg hover:bg-amber-400 transition duration-200 shadow-md disabled:bg-gray-500 disabled:text-gray-300";

    return (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4">
            <div className="bg-gray-800 rounded-xl shadow-2xl p-8 w-full max-w-sm">
                
                <h3 className="text-3xl font-extrabold text-amber-500 mb-6 text-center">
                    User Login
                </h3>

                {authFeedback && (
                    <p className="p-3 mb-4 rounded-lg text-sm text-center font-semibold bg-red-900/50 text-red-300 border border-red-700">
                        {authFeedback}
                    </p>
                )}

                <form onSubmit={handleAuthSubmit} className="space-y-4">
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className={inputClass}
                            placeholder="username"
                            disabled={isLoading}
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={inputClass}
                            placeholder="••••••••"
                            disabled={isLoading}
                        />
                    </div>
                    
                    <button
                        type="submit"
                        className={buttonClass}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Processing...' : 'Login'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AuthModal;