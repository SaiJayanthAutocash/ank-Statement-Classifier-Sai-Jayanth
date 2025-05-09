import React, { useState, useEffect, useCallback } from 'react';
import FileUpload from './components/FileUpload';
import TransactionTable from './components/TransactionTable';
import SpendingChart from './components/SpendingChart';
import { getTransactions, getMonthlySummary, getCurrentUser, login, register, logout } from './services/api';
import { Container, Typography, Box, Select, MenuItem, FormControl, InputLabel, Button, Grid, AppBar, Toolbar, Paper } from '@mui/material';

function App() {
    const [transactions, setTransactions] = useState([]);
    const [transactionsLoading, setTransactionsLoading] = useState(false);
    const [transactionsError, setTransactionsError] = useState('');

    const [summaryData, setSummaryData] = useState([]);
    const [summaryMonth, setSummaryMonth] = useState('');
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);

    const [currentUser, setCurrentUser] = useState(null);
    const [authError, setAuthError] = useState('');
    const [showLogin, setShowLogin] = useState(true);
    const [successMessage, setSuccessMessage] = useState('');

    const fetchTransactions = useCallback(async () => {
        setTransactionsLoading(true);
        setTransactionsError('');
        try {
            const response = await getTransactions({ skip: 0, limit: 200 });
            setTransactions(response.data);
        } catch (err) {
            console.error('Error fetching transactions:', err);
            setTransactionsError(err.response?.data?.detail || 'Failed to fetch transactions.');
            if (err.response?.status === 401) {
                handleLogout();
            }
        } finally {
            setTransactionsLoading(false);
        }
    }, []);

    const fetchSummary = useCallback(async (year, month) => {
        setSummaryData([]);
        try {
            const response = await getMonthlySummary(year, month);
            setSummaryData(response.data.summary);
            setSummaryMonth(response.data.month);
        } catch (err) {
            console.error('Error fetching summary:', err);
            if (err.response?.status === 401) {
                handleLogout();
            }
        }
    }, []);

    const handleLogin = async (credentials) => {
        setAuthError('');
        try {
            await login(credentials);
            const userResponse = await getCurrentUser();
            setCurrentUser(userResponse.data);
            fetchTransactions();
            fetchSummary(selectedYear, selectedMonth);
        } catch (err) {
            setAuthError(err.response?.data?.detail || 'Login failed.');
            console.error("Login error: ", err);
        }
    };

    const handleRegister = async (userData) => {
        setAuthError('');
        try {
            await register(userData);
            setSuccessMessage("Registration successful! Please log in.");
            setShowLogin(true);
        } catch (err) {
            setAuthError(err.response?.data?.detail || 'Registration failed.');
            console.error("Registration error: ", err);
        }
    };

    const handleLogout = () => {
        logout();
        setCurrentUser(null);
        setTransactions([]);
        setSummaryData([]);
    };

    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (token) {
            const fetchUserAndData = async () => {
                try {
                    const userResponse = await getCurrentUser();
                    setCurrentUser(userResponse.data);
                    fetchTransactions();
                    fetchSummary(selectedYear, selectedMonth);
                } catch (e) {
                    console.error("Session expired or invalid", e);
                    handleLogout();
                }
            };
            fetchUserAndData();
        }
    }, [fetchTransactions, fetchSummary, selectedYear, selectedMonth]);

    useEffect(() => {
        if (currentUser) {
            fetchSummary(selectedYear, selectedMonth);
        }
    }, [selectedYear, selectedMonth, fetchSummary, currentUser]);

    const handleMonthYearChange = () => {
        if (currentUser) {
            fetchSummary(selectedYear, selectedMonth);
        }
    };

    const AuthSection = () => {
        const [username, setUsername] = useState('');
        const [password, setPassword] = useState('');

        const handleSubmit = (e) => {
            e.preventDefault();
            if (showLogin) {
                handleLogin({ username, password });
            } else {
                handleRegister({ username, password });
            }
        };

        return (
            <Container maxWidth="xs" sx={{ mt: 4 }}>
                <Paper elevation={3} sx={{ p: 3 }}>
                    <Typography variant="h5" align="center" gutterBottom>
                        {showLogin ? 'Login' : 'Register'}
                    </Typography>
                    {authError && <Alert severity="error" sx={{ mb: 2 }}>{authError}</Alert>}
                    {successMessage && !authError && <Alert severity="success" sx={{ mb: 2 }}>{successMessage}</Alert>}
                    <form onSubmit={handleSubmit}>
                        <TextField
                            label="Username"
                            variant="outlined"
                            fullWidth
                            margin="normal"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                        <TextField
                            label="Password"
                            type="password"
                            variant="outlined"
                            fullWidth
                            margin="normal"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
                            {showLogin ? 'Login' : 'Register'}
                        </Button>
                        <Button color="secondary" fullWidth sx={{ mt: 1 }} onClick={() => { setShowLogin(!showLogin); setAuthError(''); setSuccessMessage('');}}>
                            {showLogin ? 'Need an account? Register' : 'Have an account? Login'}
                        </Button>
                    </form>
                </Paper>
            </Container>
        );
    };

    if (!currentUser && localStorage.getItem('authToken')) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><CircularProgress /></Box>;
    }

    if (!currentUser) {
        return <AuthSection />;
    }

    return (
        <>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Bank Statement Classifier
                    </Typography>
                    <Typography sx={{ mr: 2 }}>Hi, {currentUser.username}!</Typography>
                    <Button color="inherit" onClick={handleLogout}>Logout</Button>
                </Toolbar>
            </AppBar>
            <Container maxWidth="lg" sx={{ mt: 3 }}>
                <FileUpload onUploadSuccess={() => { fetchTransactions(); fetchSummary(selectedYear, selectedMonth); }} />

                <Box sx={{ my: 3 }}>
                    <Typography variant="h5" gutterBottom>View Summary</Typography>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item>
                            <FormControl size="small">
                                <InputLabel>Year</InputLabel>
                                <Select
                                    value={selectedYear}
                                    label="Year"
                                    onChange={(e) => setSelectedYear(e.target.value)}
                                >
                                    {[...Array(10)].map((_, i) => (
                                        <MenuItem key={new Date().getFullYear() - 5 + i} value={new Date().getFullYear() - 5 + i}>
                                            {new Date().getFullYear() - 5 + i}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item>
                            <FormControl size="small">
                                <InputLabel>Month</InputLabel>
                                <Select
                                    value={selectedMonth}
                                    label="Month"
                                    onChange={(e) => setSelectedMonth(e.target.value)}
                                >
                                    {[...Array(12)].map((_, i) => (
                                        <MenuItem key={i + 1} value={i + 1}>
                                            {new Date(0, i).toLocaleString('default', { month: 'long' })}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>
                    <SpendingChart summaryData={summaryData} month={summaryMonth} />
                </Box>

                <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>Transactions</Typography>
                <TransactionTable
                    transactions={transactions}
                    onCategoryUpdate={fetchTransactions}
                    isLoading={transactionsLoading}
                    error={transactionsError}
                />
            </Container>
        </>
    );
}

export default App;
