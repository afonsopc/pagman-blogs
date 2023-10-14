import React, { useState } from 'react'
import { Link } from "react-router-dom"
import { signupRequest } from "../App.jsx"

const Signup = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [passwordInputState, setPasswordInputState] = useState("password");
  const [responseReceived, setResponseReceived] = useState(true);

  const togglePasswordVisibility = () => {
    setPasswordInputState(passwordInputState === "password" ? "text" : "password")
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log("recieved false");
    setResponseReceived(false);
    console.log("sending request");
    const response = await signupRequest(username, email, password);
    console.log("after request");
    setResponseMessage(response.message);
    console.log("responce true");
    setResponseReceived(true);
  };
  
  return (
    <div className="auth-container">
      <form onSubmit={handleSubmit}>
        <label><h1>Sign up</h1></label>
        <input type="text" autoComplete="username" placeholder="Enter your username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input type="email" autoComplete="username" placeholder="Enter your e-mail" value={email} onChange={(e) => setEmail(e.target.value)} />
        <div className="password-container">
          <input type={passwordInputState} autoComplete="new-password" placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <span onClick={() => togglePasswordVisibility()} className="toggle-password">👁</span>
        </div>
        <button type="submit" disabled={!responseReceived}>Sign up</button>
        <span className="info">{responseMessage}</span>
        <span>Already have an account? <Link to="/login">Log in</Link></span>
      </form> 
    </div>
  )
}

export default Signup