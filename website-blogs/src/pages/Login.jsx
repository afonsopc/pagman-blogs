import React, { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { loginRequest } from "../App.jsx"

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordInputState, setPasswordInputState] = useState("password");
  const [responseMessage, setResponseMessage] = useState("");
  const [remember, setRemember] = useState(true);
  const navigate = useNavigate();


  const togglePasswordVisibility = () => {
    setPasswordInputState(passwordInputState === "password" ? "text" : "password")
  }

  const handleCheckboxChange = (event) => {
    setRemember(event.target.checked);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const data = await loginRequest(email, password)
    setResponseMessage(data.message);
    if (!data.token) {
      return
    }
    if (remember) {
      localStorage.setItem("token", data.token);
    }
    else {
      sessionStorage.setItem("token", data.token)
    }
    navigate("/")
  };
  
  return (
    <div className="auth-container">
      <form onSubmit={handleSubmit}>
        <label><h1>Log in</h1></label>
        <input type="email" autoComplete="email" placeholder="Enter your e-mail" value={email} onChange={(e) => setEmail(e.target.value)} />
        <div className="password-container">
          <input type={passwordInputState} autoComplete="current-password" placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <span onClick={() => togglePasswordVisibility()} className="toggle-password">👁</span>
        </div>
        <div className="remember-container">
          <input type="checkbox" checked={remember} onChange={handleCheckboxChange}/>
          <span className="remember-text">Remember me</span>
        </div>
        <button type="submit">Log in</button>
        <span className="info">{responseMessage}</span>
        <span>Don't have an account? <Link to="/signup">Sign up</Link></span>
      </form> 
    </div>
  )
}

export default Login