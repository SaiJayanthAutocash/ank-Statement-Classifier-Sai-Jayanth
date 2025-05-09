import React, { useState } from 'react';
import { updateTransactionCategory } from '../services/api';
import {
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
    Select, MenuItem, CircularProgress, Typography, Box, Alert
} from '@mui/material';

const categories = [
    "Uncategorized", "Food & Drink", "Transport", "Shopping",
    "Housing", "Utilities", "Entertainment", "Healthcare",
    "Education", "Income", "Other"
];

function TransactionTable({ transactions, onCategoryUpdate, isLoading, error }) {
    const [editingId, setEditingId] = useState(null);

    const handleCategoryChange = async (transactionId, newCategory) => {
        setEditingId(transactionId);
        try {
            await updateTransactionCategory(transactionId, newCategory);
            if (onCategoryUpdate) {
                onCategoryUpdate();
            }
        } catch (err) {
            console.error('Error updating category:', err);
            alert(`Failed to update category: ${err.response?.data?.detail || err.message}`);
        } finally {
            setEditingId(null);
        }
    };

    if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}><CircularProgress /></Box>;
    if (error) return <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>;
    if (!transactions || transactions.length === 0) return <Typography sx={{ my: 2 }}>No transactions to display.</Typography>;

    return (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table aria-label="transactions table">
                <TableHead>
                    <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell>Category</TableCell>
                        <TableCell>Raw Text</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {transactions.map((transaction) => (
                        <TableRow key={transaction.id}>
                            <TableCell>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                            <TableCell>{transaction.description}</TableCell>
                            <TableCell align="right" sx={{ color: transaction.amount < 0 ? 'red' : 'green' }}>
                                {transaction.amount.toFixed(2)}
                            </TableCell>
                            <TableCell>
                                {editingId === transaction.id ? <CircularProgress size={20} /> : (
                                    <Select
                                        value={transaction.category}
                                        onChange={(e) => handleCategoryChange(transaction.id, e.target.value)}
                                        size="small"
                                        variant="standard"
                                        sx={{ minWidth: 150 }}
                                    >
                                        {categories.map((cat) => (
                                            <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                                        ))}
                                    </Select>
                                )}
                            </TableCell>
                            <TableCell>{transaction.raw_text}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default TransactionTable;
