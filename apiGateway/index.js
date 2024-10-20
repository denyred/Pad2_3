const express = require('express');
const axios = require('axios');
const { createClient } = require('redis');
const app = express();

// Middleware to parse JSON body
app.use(express.json());

// Load environment variables
require('dotenv').config();

const EXTERNAL_PORT = process.env.EXTERNAL_PORT || 8081;
const INTERNAL_PORT = process.env.INTERNAL_PORT || 8080;
const SERVICE_REST_PORT = process.env.SERVICE_REST_PORT || 8000;
const TIMEOUT_MS = parseInt(process.env.TIMEOUT_MS) || 2000;
const TASK_LIMIT_PER_SERVICE = parseInt(process.env.TASK_LIMIT_PER_SERVICE) || 10;
const LOAD_THRESHOLD_PER_S_PER_SERVICE = parseInt(process.env.LOAD_THRESHOLD_PER_S_PER_SERVICE) || 5;
const MAX_TIMOUTS = parseInt(process.env.MAX_TIMOUTS) || 3;

// Redis client setup
const redisClient = createClient({ url: process.env.SM_REDIS_URL });
redisClient.connect().catch(console.error);

// Track round-robin states
let rrIndexAuth = 0;
let rrIndexChat = 0;

// Middleware to limit tasks per IP
async function limitTasks(serviceType, ip) {
    const taskKey = `tasks:${ip}`;
    const currentTasks = await redisClient.get(taskKey);

    if (currentTasks && parseInt(currentTasks) >= TASK_LIMIT_PER_SERVICE) {
        throw new Error('Task limit reached');
    }

    await redisClient.incr(taskKey);
    return taskKey;
}

// Middleware to alert on excessive load
async function alertOnLoad(serviceType, ip) {
    const loadKey = `load:${ip}`;

    // Check the current load count
    const currentLoad = await redisClient.get(loadKey);

    // If the current load is 0, set it to 1 and define the expiration
    if (currentLoad === null) {
        await redisClient.set(loadKey, 1, 'EX', 1); // Set load to 1 and expire after 1 second
    } else {
        await redisClient.incr(loadKey); // Increment if already set
    }

    // Check if the current load exceeds the threshold
    if (currentLoad && parseInt(currentLoad) >= LOAD_THRESHOLD_PER_S_PER_SERVICE) {
        console.log(`ALERT: Load on ${serviceType} [${ip}] has exceeded ${LOAD_THRESHOLD_PER_S_PER_SERVICE} req/s`);
    }
}

// Middleware to implement a simple round-robin load balancer
async function getNextIp(serviceType) {
    const key = `services:${serviceType}`;
    const ips = await redisClient.lRange(key, 0, -1);

    if (!ips || ips.length === 0) {
        throw new Error(`No available ${serviceType} instances`);
    }

    let nextIp;
    if (serviceType === 'authen') {
        nextIp = ips[rrIndexAuth % ips.length];
        rrIndexAuth++;
    } else if (serviceType === 'chat') {
        nextIp = ips[rrIndexChat % ips.length];
        rrIndexChat++;
    }

    return nextIp;
}

// Middleware to handle circuit breaker
async function handleCircuitBreaker(serviceType, ip) {
    const breakerKey = `circuit:${ip}`;

    // Check the current failure count
    const currentFailures = await redisClient.get(breakerKey);

    // If the current failure count is null, set it to 1 and define the expiration
    if (currentFailures === null) {
        await redisClient.set(breakerKey, 1, 'EX', TIMEOUT_MS * 4); // Set failures to 1 and expire after TIMEOUT_MS * 4
    } else {
        await redisClient.incr(breakerKey); // Increment if already set
    }

    // Check if the current failures exceed the threshold
    if (currentFailures && parseInt(currentFailures) + 1 >= MAX_TIMOUTS) {
        console.log(`ALERT: ${ip} has failed to respond in adequate time ${parseInt(currentFailures) + 1} times within ${TIMEOUT_MS * MAX_TIMOUTS} ms`);
    }
}

// Status endpoint
app.get('/status', (req, res) => {
    res.status(200).json({ message: `API Gateway running at http://127.0.0.1:${EXTERNAL_PORT} is alive!` });
});

// Route handler for authentication service
app.all('/authen/*', async (req, res) => {
    let ip;
    try {
        ip = await getNextIp('authen');
        await limitTasks('authen', ip);
        await alertOnLoad('authen', ip);

        const endpoint = req.url.replace('/authen/', '');
        const url = `http://${ip}:${SERVICE_REST_PORT}/${endpoint}`;
        const response = await axios({
            method: req.method,
            url: url,
            data: req.body,
            headers: req.headers,
            timeout: TIMEOUT_MS
        });

        res.status(response.status).send(response.data);
    } catch (error) {
        console.error(`Error on /authen:`, error.message);
        if (error.code === 'ECONNABORTED') {
            if (ip) await handleCircuitBreaker('authen', ip);
            res.status(504).send({ detail: `Request passed to ${ip} has timed out.` });
        } else if (error.message === 'Task limit reached') {
            res.status(503).send({ detail: `Service at ${ip} is too busy to process the request passed.` });
        } else if (error.message === 'No available authen instances') {
            res.status(503).send({ detail: "No available authenService instances." });
        } else {
            // Extract details from the error response if it exists
            const errorResponse = error.response?.data || { detail: error.message };

            // Forward the status code and error details from the service
            res.status(error.response?.status || 500).json(errorResponse);
        }
    } finally {
        if (ip) {
            await redisClient.decr(`tasks:${ip}`);
        }
    }
});

// Route handler for chat service
app.all('/chat/*', async (req, res) => {
    let ip;
    try {
        ip = await getNextIp('chat');
        await limitTasks('chat', ip);
        await alertOnLoad('chat', ip);

        const endpoint = req.url.replace('/chat/', '')
        const url = `http://${ip}:${SERVICE_REST_PORT}/${endpoint}`;
        const response = await axios({
            method: req.method,
            url: url,
            data: req.body,
            headers: req.headers,
            timeout: TIMEOUT_MS
        });

        res.status(response.status).send(response.data);
    } catch (error) {
        console.error(`Error on /chat:`, error.message);
        if (error.code === 'ECONNABORTED') {
            if (ip) await handleCircuitBreaker('chat', ip);
            res.status(504).send({ detail: `Request passed to ${ip} has timed out.` });
        } else if (error.message === 'Task limit reached') {
            res.status(503).send({ detail: `Service at ${ip} is too busy to process the request passed.` });
        } else if (error.message === 'No available chat instances') {
            res.status(503).send({ detail: "No available chatService instances." });
        } else {
            // Extract details from the error response if it exists
            const errorResponse = error.response?.data || { detail: error.message };

            // Forward the status code and error details from the service
            res.status(error.response?.status || 500).json(errorResponse);
        }
    } finally {
        if (ip) {
            await redisClient.decr(`tasks:${ip}`);
        }
    }
});

// Start server
app.listen(INTERNAL_PORT, () => {
    console.log(`Gateway running on port ${EXTERNAL_PORT}`);
});

// Graceful shutdown logic
const shutdown = async () => {
    console.log('Graceful shutdown initiated...');

    // Stop accepting new requests
    server.close(async (err) => {
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