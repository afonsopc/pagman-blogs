import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom';
import { createOperation, getUserInfo } from '../App';

const AccountPage = () => {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [emailRequest, setEmailRequest] = useState({})
    const [usernameRequest, setUsernameRequest] = useState({})
    const [newPasswordRequest, setNewPasswordRequest] = useState({})
    const [deleteRequest, setDeleteRequest] = useState({})
    const [oldUserInfo, setOldUserInfo] = useState()
    const [newPassword, setNewPassword] = useState("")
    const [newPasswordInputState, setNewPasswordInputState] = useState("password");
    const popUpRef = useRef(null);
    const navigate = useNavigate();
  
  
    useEffect(() => {
      const fetchData = async () => {
        const userInfoRequest = await getUserInfo();
        if ("username" in userInfoRequest) {
          setOldUserInfo(userInfoRequest)
          setUsername(userInfoRequest.username);
          setEmail(userInfoRequest.email)
        }
        else {
          navigate(`/login`)
        }
      };
  
      fetchData();
    }, [])

  
  const applyChanges = async () => {
    let changes = false
    if (email !== oldUserInfo.email && email !== "") {
      let operationRequest = await createOperation("email", email)
      setEmailRequest(operationRequest)
      console.log(operationRequest);
      changes = true
    }
    if (username !== oldUserInfo.username && username !== "") {
      let operationRequest = await createOperation("username", username)
      setUsernameRequest(operationRequest)
      console.log(operationRequest);
      changes = true
    }
    if (newPassword !== "") {
      let operationRequest = await createOperation("password", newPassword)
      setNewPasswordRequest(operationRequest)
      console.log(operationRequest);
      changes = true
    }
    return changes
  }
  
  const openPopUp = () => {
    popUpRef.current.style.display = 'flex';
  }

  const closePopUp = () => {
    popUpRef.current.style.display = 'none';
  }
  
  const onDeleteAccountButtonClick = async () => {
    let operationRequest = await createOperation("delete", "")
    setDeleteRequest(operationRequest)
    console.log(operationRequest)
    openPopUp()
  }

  const onApplyButtonClick = async () => {
    const changes = await applyChanges()
    console.log(changes);
    if (changes) {
      openPopUp()
    }
  }

  return (
    <div className="account-page-container">
      <div ref={popUpRef} className="pop-up-background-container">
        <div className="pop-up-container">
          <div className="requests-container">
            {Object.keys(emailRequest).length !== 0 ? (
              <div>
                <h2>Email Request:</h2>
                <p>{emailRequest.message}</p>
              </div>
            ) : null}
            {Object.keys(usernameRequest).length !== 0 ? (
              <div>
                <h2>Username Request:</h2>
                <p>{usernameRequest.message}</p>
              </div>
            ) : null}
            {Object.keys(newPasswordRequest).length !== 0 ? (
              <div>
                <h2>New Password Request:</h2>
                <p>{newPasswordRequest.message}</p>
              </div>
            ) : null}
            {Object.keys(deleteRequest).length !== 0 ? (
              <div>
                <h2>Delete Request:</h2>
                <p>{deleteRequest.message}</p>
              </div>
            ) : null}
          </div>
          <button onClick={() => closePopUp()} className="ok-button">Ok</button>
        </div>
      </div>
      <div className="settings-container">
        <div className="account-settings-title">
            <h1 id="title">Account Settings</h1>
        </div>
        <hr/>
        <div className="account-settings-container">
            <div className="edit-account-info-container">
                {/* E-Mail */}
                <h3>Change your e-mail</h3>
                <input type="email" placeholder="E-Mail" value={email} onChange={(e) => setEmail(e.target.value)} />
                {/* Username */}
                <h3>Change your username</h3>
                <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                {/* Password */}
                <h3>Change your password</h3>
                <div className="password-change-container">
                    <div className="password-container">
                      <input type={newPasswordInputState} placeholder="New Password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
                      <span onClick={() => setNewPasswordInputState(newPasswordInputState === "password" ? "text" : "password")} className="toggle-password">👁</span>
                    </div>
                </div>
            </div>
            <div className="apply-container">
                <button onClick={() => onApplyButtonClick()} id="apply-button">Apply Changes</button>
            </div>
            <hr/>
            <div className="delete-account-container">
                <label>Delete your account?</label>
                <button onClick={() => onDeleteAccountButtonClick()} id="delete-account-button">Delete account</button>
            </div>
        </div>
      </div>
    </div>
  )
}

export default AccountPage