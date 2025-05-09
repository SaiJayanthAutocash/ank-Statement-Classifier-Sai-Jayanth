import React, { useState } from 'react';
import { uploadTransactionsCSV } from '../services/api';
import { Button, CircularProgress, Typography, Box, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

function FileUpload({ onUploadSuccess }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setError('');
        setSuccessMessage('');
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a file first.');
            return;
        }
        setIsLoading(true);
        setError('');
        setSuccessMessage('');
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await uploadTransactionsCSV(formData);
            setSuccessMessage(response.data.message || 'File uploaded and processed successfully!');
            if (onUploadSuccess) {
                onUploadSuccess();
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Error uploading file. Please ensure it is a valid CSV.');
            console.error('Upload error:', err);
        } finally {
            setIsLoading(false);
            setSelectedFile(null);
        }
    };

    return (
        <Box sx={{ my: 2, p: 2, border: '1px dashed grey', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>Upload CSV Statement</Typography>
            <input
                accept=".csv"
                style={{ display: 'none' }}
                id="raised-button-file"
                type="file"
                onChange={handleFileChange}
                key={selectedFile ? selectedFile.name : 'empty'}
            />
            <label htmlFor="raised-button-file">
                <Button variant="outlined" component="span" startIcon={<CloudUploadIcon />}>
                    {selectedFile ? selectedFile.name : "Choose File"}
                </Button>
            </label>
            <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!selectedFile || isLoading}
                sx={{ ml: 2 }}
            >
                {isLoading ? <CircularProgress size={24} /> : 'Upload'}
            </Button>
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            {successMessage && <Alert severity="success" sx={{ mt: 2 }}>{successMessage}</Alert>}
        </Box>
    );
}

export default FileUpload;
