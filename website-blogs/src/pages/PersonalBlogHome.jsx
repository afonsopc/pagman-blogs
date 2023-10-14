import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getBlogs, getUserInfo, unixTimeToDate } from '../App';


const PersonalBlogHome = () => {
    const { author } = useParams();
    const authorClear = author.replace(/-/g, " ")
    const [receivedBlogs, setReceivedBlogs] = useState([])
    const [receivedBlogsRequest, setReceivedBlogsRequest] = useState(false)
    const [responseReceived, setResponseReceived] = useState(false)
    const [amountOfBlogsToLoad, setAmountOfBlogsToLoad] = useState(10)
    const [username, setUsername] = useState("");

    const fetchBlogs = async (amount) => {
        setResponseReceived(false)
        setReceivedBlogsRequest(false)
        const blogRequest = await getBlogs(authorClear, amount);
        const userInfoRequest = await getUserInfo();
        if ("username" in userInfoRequest) {
            setUsername(userInfoRequest.username);
        }
        if ("blogs" in blogRequest) {
            setReceivedBlogs(blogRequest.blogs)
            setReceivedBlogsRequest(true)
        }
        setResponseReceived(true)
    };

    useEffect(() => {
        fetchBlogs(amountOfBlogsToLoad);
    }, [])

    const loadMore = () => {
        const newAmountOfBlogsToLoad = amountOfBlogsToLoad+10;
        fetchBlogs(newAmountOfBlogsToLoad);
        setAmountOfBlogsToLoad(newAmountOfBlogsToLoad);
    }

    return (
        <div className="personal-blog-home-container">
            <div className="username-title-container">
                <h1><span id="username">{authorClear}</span>'s Blog Page</h1>
            </div>
            <div className="blogs-container">
                {receivedBlogsRequest ? (
                    <div className="blogs-list-container">
                        {receivedBlogs.map((blog) => (
                            <div className="blogs-item-container" key={blog.blog_id}>
                                <Link to={`/blogs/${authorClear}/${blog.blog_id}`}>
                                    <h2>{blog.blog_title ? blog.blog_title : "Untitled"}</h2>
                                </Link>
                                <p>{unixTimeToDate(blog.unix_time)}</p>
                            </div>
                        )) }
                        <button id="load-more-button" onClick={loadMore} style={{display: (receivedBlogs.length >= 10) ? "block" : "none"}}>Load More 10</button>
                    </div>
                ) : (
                    <div className="status-text-container">
                        <h1 id="status-text" >{responseReceived ? "This user doesn't have any blogs posted." : "Loading..."}</h1>
                    </div>
                )}
            </div>
        </div>
    )
    }

export default PersonalBlogHome