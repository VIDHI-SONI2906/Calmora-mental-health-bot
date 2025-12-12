🌿 Calmora – Mental Health Chatbot:- 

A supportive AI chatbot built using React (Frontend) and Python (Backend).

Calmora is a mental-health assistant designed to provide supportive, empathetic conversations.
It allows users to chat directly with an AI model through a clean React UI, while the backend processes the conversation using NLP utilities.

⭐ Features

🌱 Friendly, supportive mental-health chatbot
💬 Real-time chat through a React frontend
🧠 NLP-powered backend built in Python
🔧 Custom NLU utilities for intent and response generation
🗂️ Clean separation of frontend and backend
🚀 Lightweight and easy to run


📁 Project Structure
Calmora/
│
├── backend/
│   ├── app.py
│   ├── nlu_utils.py
│   ├── requirements.txt
│   ├── instance/
│   ├── migrations/
│   ├── knowledge/
│   └── venv/ (ignored)
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── node_modules/ (ignored)
│
├── README.md
└── .gitignore


🛠️ Tech Stack

1. Frontend

React.js
HTML / CSS
JavaScript

2. Backend

Python
Flask / FastAPI (based on your setup)
NLP Utilities (nlu_utils.py)


🚀 How to Run the Project
1. Clone the repository
-> git clone https://github.com/VIDHI-SONI2906/Calmora-mental-health-bot.git
-> cd calmora-mental-health-chatbot

🟦 FRONTEND SETUP (React)
2. Move inside frontend folder
-> cd frontend

3. Install dependencies
-> npm install

4. Start the React app
-> npm start


Your frontend will run on:
👉 http://localhost:3000

🟩 BACKEND SETUP (Python)
5. Move to backend
-> cd ../backend

6. Create virtual environment
-> python -m venv venv

7. Activate it

Windows:

-> venv\Scripts\activate

8. Install backend dependencies
-> pip install -r requirements.txt

9. Run backend server
-> python app.py


Backend runs on something like:
👉 http://localhost:5000

🔗 Connecting Frontend & Backend

Your React app should send requests to your backend API routes (usually /chat, /predict, etc.).
Make sure API URL in App.js or service file matches your backend URL.


👤 Author

Vidhi Soni – AI/ML , Python & NLP Enthusiast