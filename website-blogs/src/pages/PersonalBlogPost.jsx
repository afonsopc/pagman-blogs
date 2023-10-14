import React, { useEffect } from 'react'
import { useState } from 'react';
import { useParams } from 'react-router-dom'
import { getBlog, unixTimeToDate } from '../App';
import DOMPurify from 'dompurify';
import parse from "html-react-parser";

const PersonalBlogPost = () => {
  const { author, id } = useParams();
  const [blogHtml, setBlogHtml] = useState("")
  const [unixTime, setUnixTime] = useState()
  const [blogTitle, setBlogTitle] = useState("")
  const [authorClean, setAuthorClean] = useState(author.replace(/-/g, " "));

  useEffect(() => {
    getBlog(authorClean, id)
      .then((request) => {
        setUnixTime(request.unix_time);
        setBlogTitle(request.blog_title)
        const dirtyHtmlString = request.blog_html
        let clean = DOMPurify.sanitize(dirtyHtmlString, {USE_PROFILES: {html: true}});
        setBlogHtml(request.blog_html)
      })
      .catch((error) => {
        console.error("Error fetching blog post:", error);
      });
  }, [authorClean, id]);
  return (
    <div className="personal-blog-post-container">
        <div className="blog-container">
          <div className="blog-title-container">
            <div className="blog-date-container">
              <span>{unixTimeToDate(unixTime)}</span>
            </div>
            <h1 id="title">{blogTitle}</h1>
          </div>
          <div className="blog-html-container">
            {parse(blogHtml)}
          </div>
        </div>
    </div>

  )
}

export default PersonalBlogPost