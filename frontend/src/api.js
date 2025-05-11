// API client for authentication and transactions
import axios from 'axios';

const API_BASE_URL = '/api/v1';

// Authentication API
export const authApi = {
    login: async (username, password) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/token`, {
                username,
                password
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    },

    register: async (username, password) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/register`, {
                username,
                password
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    },

    getCurrentUser: async (token) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/auth/me`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    }
};

// Transaction API
export const transactionApi = {
    uploadCsv: async (file, token) => {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await axios.post(`${API_BASE_URL}/transactions/upload-csv/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${token}`
                }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    },

    getTransactions: async (skip = 0, limit = 100, token) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/transactions/`, {
                headers: {
                    Authorization: `Bearer ${token}`
                },
                params: {
                    skip,
                    limit
                }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    },

    updateCategory: async (transactionId, category, token) => {
        try {
            const response = await axios.put(`${API_BASE_URL}/transactions/${transactionId}/category`, {
                category
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    },

    getMonthlySummary: async (year, month, token) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/transactions/summary/${year}/${month}`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    }
};

// Auth context for managing authentication state
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));

    const login = async (username, password) => {
        const response = await authApi.login(username, password);
        setToken(response.access_token);
        localStorage.setItem('token', response.access_token);
        const userData = await authApi.getCurrentUser(response.access_token);
        setUser(userData);
        return userData;
    };

    const register = async (username, password) => {
        const response = await authApi.register(username, password);
        return response;
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
    };

    useEffect(() => {
        if (token) {
            authApi.getCurrentUser(token)
                .then(userData => setUser(userData))
                .catch(error => {
                    console.error('Error fetching user data:', error);
                    logout();
                });
        }
    }, [token]);

    return (
        <AuthContext.Provider value={{
            user,
            token,
            login,
            register,
            logout,
            isAuthenticated: !!token
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
