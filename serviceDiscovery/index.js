const express = require('express');
const { createClient } = require('redis');
const app = express();

// Load environment variables
require('dotenv').config();

const EXTERNAL_PORT = process.env.EXTERNAL_PORT || 8081;
const INTERNAL_PORT = process.env.INTERNAL_PORT || 8080;

// Redis client setup
const redisClient = createClient({ url: process.env.SM_REDIS_URL });
redisClient.connect().catch(console.error);

// Middleware to parse JSON body
app.use(express.json());

// Status endpoint
app.get('/status', (req, res) => {
    res.status(200).json({ message: `Service discovery running at http://127.0.0.1:${EXTERNAL_PORT} is alive!` });
});

// Route to register services
app.post('/register', async (req, res) => {
    const { host, type } = req.body;

    if (!host || !type) {
        return res.status(400).json({ detail: 'Host and service type are required.' });
    }

    try {
        const key = `services:${type}`;
        // Add the host to the array if it doesn't already exist
        await redisClient.lPushX(key, host);
        
        // In case the list does not exist, ensure to create it with lPush
        const listExists = await redisClient.exists(key);
        if (!listExists) {
            await redisClient.lPush(key, host);
        }

        res.status(200).json({ message: `Service registered: ${host} as ${type}` });
    } catch (err) {
        console.error('Error registering service:', err);
        res.status(500).json({ detail: 'Failed to register service.' });
    }
});

// Start server
app.listen(INTERNAL_PORT, () => {
    console.log(`Service discovery app running on port ${EXTERNAL_PORT}`);
});

// Graceful shutdown logic
const shutdown = async () => {
    console.log('Graceful shutdown initiated...');

    // Stop accepting new requests
    server.close(async err => {
        if (err) {
            console.error('Error closing the server:', err);
            process.exit(1);
        }

        console.log('Server closed.');

        // Disconnect Redis client
        try {
            await redisClient.quit();
            console.log('Redis client disconnected.');
        } catch (redisErr) {
            console.error('Error disconnecting Redis client:', redisErr);
        }

        // Exit the process
        process.exit(0);
    });
};

// Listen for shutdown signals
process.on('SIGTERM', shutdown);    // Sent by Docker, Kubernetes
process.on('SIGINT', shutdown);     // Ctrl+C in terminal