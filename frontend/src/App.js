import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [view, setView] = useState("login"); 
  const [message, setMessage] = useState("");
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [registerForm, setRegisterForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: ""
  });
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  // Check session status on load
  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch("http://localhost:5000/session-status", {
          method: "GET",
          credentials: "include",
        });
        const data = await res.json();
        if (data.logged_in) {
          setView("chat");
        }
      } catch (err) {
        console.error("Session check failed:", err);
      }
    };
    checkSession();
  }, []);

  // Add initial greeting when chat view is loaded
  useEffect(() => {
    if (view === "chat" && chatHistory.length === 0) {
      setChatHistory([
        { sender: "Advisor", text: "Hello, how are you feeling?" }
      ]);
    }
  }, [view]);

  const handleLogin = async () => {
    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(loginForm),
      });
      const data = await response.json();
      if (response.ok) {
        setMessage("Login successful.");
        setView("chat");
      } else {
        setMessage(data.message || "Login failed.");
      }
    } catch (err) {
      console.error(err);
      setMessage("Login error.");
    }
  };

  const handleRegister = async () => {
    try {
      const response = await fetch("http://localhost:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(registerForm),
      });
      const data = await response.json();
      if (response.ok) {
        setMessage("Registration successful. Please log in.");
        setView("login");
      } else {
        setMessage(data.message || "Registration failed.");
      }
    } catch (err) {
      console.error(err);
      setMessage("Registration error.");
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (input.trim() === "") return;
    setChatHistory((prev) => [...prev, { sender: "You", text: input }]);
    

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: input }),
      });
      const data = await response.json();
      setChatHistory((prev) => [...prev, { sender: "Advisor", text: data.message }]);
      setInput("");
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [
        ...prev,
        { sender: "Advisor", text: "Error: Unable to fetch response." }
      ]);
    }
  };

  const handleLogout = async () => {
    try {
      const response = await fetch("http://localhost:5000/logout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
      const data = await response.json();
      if (response.ok) {
        setMessage(data.message);
        setView("login");
        setChatHistory([]);
      } else {
        setMessage(data.message || "Logout failed.");
      }
    } catch (err) {
      console.error(err);
      setMessage("Logout error.");
    }
  };

  /*
    VIEWS: 
    1) LOGIN 
    2) REGISTER 
    3) CHAT (with separate .chat-wrapper)
  */

  // LOGIN VIEW
  if (view === "login") {
    return (
      <div className="App">
        <h1>Calmora</h1>
        {message && <p>{message}</p>}

        <div className="form-container">
          <h2>Login</h2>

          <input
            type="email"
            placeholder="Email"
            value={loginForm.email}
            onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            value={loginForm.password}
            onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
          />
          <button onClick={handleLogin}>Login</button>

          <p>
            Don't have an account?{" "}
            <button className="switch-link" onClick={() => setView("register")}>
              Register
            </button>
          </p>
        </div>
      </div>
    );
  }

  // REGISTER VIEW
  else if (view === "register") {
    return (
      <div className="App">
        <h1>Calmora</h1>
        {message && <p>{message}</p>}

        <div className="form-container">
          <h2>Register</h2>

          <input
            type="text"
            placeholder="Name"
            value={registerForm.name}
            onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
          />
          <input
            type="email"
            placeholder="Email"
            value={registerForm.email}
            onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            value={registerForm.password}
            onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
          />
          <input
            type="password"
            placeholder="Re-enter Password"
            value={registerForm.confirm_password}
            onChange={(e) =>
              setRegisterForm({ ...registerForm, confirm_password: e.target.value })
            }
          />
          <button onClick={handleRegister}>Register</button>

          <p>
            Already have an account?{" "}
            <button className="switch-link" onClick={() => setView("login")}>
              Login
            </button>
          </p>
        </div>
      </div>
    );
  }

  // CHAT VIEW 
  else if (view === "chat") {
    return (
      <div className="chat-wrapper"> 
        {/* Chat header with title (left) and logout (right) */}
        <div className="chat-header">
          <h1>Calmora</h1>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>

        {message && <p>{message}</p>}

        <div className="chat-container">
          <div className="chat-history">
            {chatHistory.map((chat, index) => (
              <div
                key={index}
                className={`message ${chat.sender === "You" ? "user" : "advisor"}`}
              >
                <strong>{chat.sender}:</strong> 
                <span style={{ whiteSpace: 'pre-line' }}>{chat.text}</span>
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="chat-form">
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit">Send</button>
          </form>
        </div>
      </div>
    );
  }

  return null;
}

export default App;