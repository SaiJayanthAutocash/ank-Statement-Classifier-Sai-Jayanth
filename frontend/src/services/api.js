import axios from 'axios';

const API_URL = '/api/v1';

const getAuthToken = () => localStorage.getItem('authToken');

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to add JWT token to requests if available
apiClient.interceptors.request.use(
    (config) => {
        const token = getAuthToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Authentication Services
export const register = (userData) => apiClient.post('/auth/register', userData);
export const login = async (credentials) => {
    const response = await apiClient.post('/auth/token', new URLSearchParams(credentials), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token);
    }
    return response.data;
};
export const logout = () => {
    localStorage.removeItem('authToken');
};
export const getCurrentUser = () => apiClient.get('/auth/users/me');

// Transaction Services
export const uploadTransactionsCSV = (formData) => {
    return apiClient.post('/transactions/upload-csv/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

export const getTransactions = (params) => {
    return apiClient.get('/transactions/', { params });
};

export const updateTransactionCategory = (transactionId, category) => {
    return apiClient.patch(`/transactions/${transactionId}/category`, { category });
};

export const getMonthlySummary = (year, month) => {
    return apiClient.get(`/transactions/summary/monthly/${year}/${month}`);
};

export default apiClient;
