const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 3000;

app.use(cors());

const categories = [
    "customer_service",
    "technical",
    "billing"
];

const statuses = ["open", "closed"];

function generateRandomTickets(count = 10) {
    return Array.from({ length: count }, (_, i) => ({
        id: i + 1,
        category: categories[Math.floor(Math.random() * categories.length)],
        status: statuses[Math.floor(Math.random() * statuses.length)]
    }));
}

app.get("/tickets", (req, res) => {
    const tickets = generateRandomTickets(10 + Math.floor(Math.random() * 5));
    res.json({ tickets });
});

app.listen(PORT, () => {
    console.log(`Mock Ticket API running at http://localhost:${PORT}`);
});
