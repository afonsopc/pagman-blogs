import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
} from "react-router-dom";
import Signup from "./pages/Signup.jsx"
import Login from "./pages/Login.jsx"
import Home from "./pages/Home.jsx"
import PersonalBlogHome from "./pages/PersonalBlogHome.jsx"
import PersonalBlogPost from "./pages/PersonalBlogPost.jsx"
import PersonalBlogWrite from "./pages/PersonalBlogWrite.jsx"
import Navbar from "./components/Navbar.jsx"
import Footer from "./components/Footer.jsx"
import MinimalNavbar from "./components/MinimalNavbar.jsx"
import "./style.scss"
import AccountPage from "./pages/AccountPage.jsx";

export const blogPostMaxSize = 8 // In MegaBytes
export const apiBranchURL = "https://api.blogs.pagman.org/v1"

export const unixTimeToDate = (unixTime) => {
  const date = new Date(unixTime * 1000)
  const hours = date.getHours().toString()
  let minutes = date.getMinutes().toString()
  if (minutes.length === 1) {
    minutes = "0" + minutes
  }
  const day = date.getDate().toString().padStart(2, "0");
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const year = date.getFullYear().toString();
  const formattedDate = `${hours}:${minutes} - ${day}/${month}/${year}`;
  return formattedDate
}

export const createOperation = async (operation, operationValue) => {
  const token = localStorage.getItem("token") || sessionStorage.getItem("token") || null;
  if (token != null) {
    const response = await fetch(`${apiBranchURL}/operation/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({"operation": operation, "operation_value": operationValue})
    });
    const data = await response.json();
    return data
  }
  return {"message": "No token in storage."}
}

export const postBlog = async (blogTitle, blogHtml) => {
  const token = localStorage.getItem("token") || sessionStorage.getItem("token") || null;
  if (token != null) {
    const response = await fetch(`${apiBranchURL}/postblog`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({"blog_title": blogTitle, "blog_html": blogHtml})
    });
    const data = await response.json();
    return data
  }
  return {"message": "No token in storage."}
};

export const getUserInfo = async () => {
  const token = localStorage.getItem("token") || sessionStorage.getItem("token") || null;
  if (token != null) {
    const response = await fetch(`${apiBranchURL}/getuserinfo`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
    });
    const data = await response.json();
    return data
  }
  return {"message": "No token in storage."}
};

export const signupRequest = async (username, email, password) => {
  console.log("sending")
  const response = await fetch(`${apiBranchURL}/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ "username": username, "email": email, "password": password })
  });
  const data = await response.json();
  console.log("recieved")
  return data
};

export const loginRequest = async (email, password) => {
  console.log("sending")
  const response = await fetch(`${apiBranchURL}/login`, {
    method: 'POST',
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ "email": email, "password": password })
  });
  const data = await response.json();
  console.log("recieved")
  return data
};

export const getBlog = async (username, blogId) => {
  const response = await fetch(`${apiBranchURL}/getblog/${username}/${blogId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  const data = await response.json();
  return data
};

export const getBlogs = async (author, amount) => {
  const response = await fetch(`${apiBranchURL}/getblogs/${author}/${amount}`, {
  method: "GET",
  headers: {
    "Content-Type": "application/json",
  },
  });
  const data = await response.json();
  return data
}

const Layout = () => {
  return (
    <>
      <Navbar/>
      <Outlet/>
      <Footer/>
    </>
  );
};

const MinimalLayout = () => {
  return (
    <>
      <MinimalNavbar/>
      <Outlet/>
      <Footer/>
    </>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout/>,
    children: [
      {
        path: "",
        element: <Home/>
      },
      {
        path: "/write",
        element: <PersonalBlogWrite/>
      },
    ]
  },
  {
    path: "/",
    element: <MinimalLayout/>,
    children: [
      {
        path: "/signup",
        element: <Signup/>
      },
      {
        path: "/login",
        element: <Login/>
      },
      {
        path: "/account",
        element: <AccountPage/>
      },
    ]
  },
  {
    path: "/blogs/:author",
    element: <Layout/>,
    children: [
      {
        path: "",
        element: <PersonalBlogHome/>
      },
      {
        path: ":id",
        element: <PersonalBlogPost/>
      },
    ]
  },
]);

function App() {
  return (
    <div className="app">
      <div className="container">
        <RouterProvider router={router} c/>
      </div>
    </div>
  )
}


export default App
