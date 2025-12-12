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
   
-> git clone https://github.com/VIDHI-SONI2906/Calmora-mental-health-bot.

-> cd calmora-mental-health-chatbot

🟦 FRONTEND SETUP (React)
2. Move inside frontend folder

-> cd frontend

3. Install dependencies
   
-> npm install

5. Start the React app
   
-> npm start


Your frontend will run on:

👉 http://localhost:3000

🟩 BACKEND SETUP (Python)

5. Move to backend
   
-> cd ../backend

7. Create virtual environment
   
-> python -m venv venv

9. Activate it

Windows:

-> venv\Scripts\activate

8. Install backend dependencies
   
-> pip install -r requirements.txt

10. Run backend server
    
-> python app.py


Backend runs on something like:

👉 http://localhost:5000
<img width="1053" height="836" alt="Screenshot 2025-12-12 225640" src="https://github.com/user-attachments/assets/402505f1-3761-4aae-b2b3-f977e059dc73" />
<img width="779" height="881" alt="Screenshot 2025-12-12 225730" src="https://github.com/user-attachments/assets/d18440b6-21f3-4197-9e5e-fb0ffa4d070f" />
<img width="1053" height="836" alt="Screenshot 2025-12-12 225640" src="https://github.com/user-attachments/assets/a43e6af4-b4e4-44a6-bab2-f09500987d19" />
<img width="1055" height="890" alt="Screenshot 2025-12-12 225834" src="https://github.com/user-attachments/assets/83824bb2-e74b-4a9a-9cb9-4c97f685b0f1" />


🔗 Connecting Frontend & Backend

Your React app should send requests to your backend API routes (usually /chat, /predict, etc.).
Make sure API URL in App.js or service file matches your backend URL.


👤 Author

Vidhi Soni – AI/ML , Python & NLP Enthusiast
