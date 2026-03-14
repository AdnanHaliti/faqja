const express = require('express');
const router = express.Router();
const { getResponse } = require('../services/openai');

// Route to handle user messages
router.post('/chat', async (req, res) => {
    const userMessage = req.body.message;

    try {
        const botResponse = await getResponse(userMessage);
        res.json({ response: botResponse });
    } catch (error) {
        console.error('Error communicating with OpenAI:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

module.exports = router;