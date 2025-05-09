import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js';
import { Typography, Box, Paper } from '@mui/material';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

function SpendingChart({ summaryData, month }) {
    if (!summaryData || summaryData.length === 0) {
        return <Typography sx={{ my: 2, textAlign: 'center' }}>No spending data available for {month || 'the selected period'}.</Typography>;
    }

    const data = {
        labels: summaryData.map(item => item.category),
        datasets: [
            {
                label: 'Spending by Category',
                data: summaryData.map(item => Math.abs(item.total_amount)),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)',
                    'rgba(83, 102, 255, 0.7)',
                    'rgba(40, 159, 64, 0.7)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(199, 199, 199, 1)',
                    'rgba(83, 102, 255, 1)',
                    'rgba(40, 159, 64, 1)',
                ],
                borderWidth: 1,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: `Spending Summary for ${month}`,
                font: { size: 16 }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed !== null) {
                            label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed);
                        }
                        return label;
                    }
                }
            }
        },
    };

    return (
        <Paper sx={{ p: 2, mt: 3 }}>
            <Box sx={{ maxWidth: '500px', margin: 'auto' }}>
                <Pie data={data} options={options} />
            </Box>
        </Paper>
    );
}

export default SpendingChart;
