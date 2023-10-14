import React, { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getUserInfo } from "../App.jsx"

const Navbar = () => {
  const { author } = useParams();
  const [loggedInState, setLoggedInState] = useState(false);
  const [username, setUsername] = useState("username");
  const [authorClean, setAuthorClean] = useState(author ? author.replace(/-/g, " "): "");
  const [userMenuState, setUserMenuState] = useState(false);
  const buttonRef = useRef(null);
  const menuRef = useRef(null);
  
  useEffect(() => {
    const fetchData = async () => {
      const userInfo = await getUserInfo();
      if ("username" in userInfo) {
        setLoggedInState(true);
        setUsername(userInfo.username);
      }
    };
  
    fetchData();
    // add event listener to document/window
    const handleClick = (event) => {
      if (
        (buttonRef.current && buttonRef.current.contains(event.target)) ||
        (menuRef.current && menuRef.current.contains(event.target))
      ) {
        // click event was triggered on the button
        setUserMenuState(true);
      } else {
        // click event was triggered elsewhere on the document/window
        setUserMenuState(false);
      }
    };
    document.addEventListener('click', handleClick);

    // cleanup function to remove event listener
    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, []);

  const logout = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.reload(true)
  };

  return (
    <div className="navbar-container">
      <div className="logo-container">
        <Link className="logo" to={author ? `/blogs/${author.replace(/\s+/g, '-')}` : "/"}><img src="/pagman_blogs_logo.webp"/><span id="logo-text">{authorClean ? `${authorClean}'s Blogs` : "Blogs"}</span></Link>
      </div>
      <div className="account-container">
        <div className="logged-in-container" style={{display: loggedInState ? "flex" : "none"}}>
          <div className="hello-container">
            <span id="hello">Hello</span> 
            <button ref={buttonRef} id="username">
              {username.split(" ").length > 1
                ? username
                    .split(" ")
                    .slice(0, 4)
                    .join(" ")
                    .length > 20
                      ? username.split(" ").slice(0, 4).join(" ").substring(0, 20) + "..."
                      : username.split(" ").slice(0, 4).join(" ")
                        + (username.split(" ").length > 4 ? "..." : "")
                : username.length > 12
                  ? username.substring(0, 12) + "..."
                  : username}
            </button>
            <div ref={menuRef} className="user-menu-container" style={{display: userMenuState ? "flex" : "none"}}>
              <div className="entry">
                <Link to={`/blogs/${username.replace(/\s+/g, '-')}`}>
                  <img className="icon" src="/open-outline.svg"/>
                  <span className="text">My Blog</span>
                </Link>
              </div>
              <div className="entry">
                <Link to={"/write"}>
                  <img className="icon" src="/add-circle-outline.svg"/>
                  <span className="text">Write and Post</span>
                </Link>
              </div>
              <div className="entry">
                <Link className="" to="/account">
                  <img className="icon" src="/cog-outline.svg"/>
                  <span className="text">My Account</span>
                </Link>
              </div>
              <div className="entry">
                <Link onClick={() => logout()}>
                  <img className="icon" src="/log-out-outline.svg"/>
                  <span className="text">Log out</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="logged-out-container" style={{display: loggedInState ? "none" : "flex"}}>
          <Link to="/login">Log in</Link>
          <Link to="/signup">Signup</Link>
        </div>
      </div>
    </div>
  )
}

export default Navbar