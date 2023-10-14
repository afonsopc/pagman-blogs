import React, { useEffect, useRef, useState } from "react";
import { Editor } from "@tinymce/tinymce-react";
import { blogPostMaxSize, getUserInfo, postBlog } from "../App";
import { useNavigate } from "react-router-dom";

const PersonalBlogWrite = () => {
  const editorRef = useRef(null)
  const [title, setTitle] = useState("")
  const [username, setUsername] = useState("")
  const navigate = useNavigate();


  useEffect(() => {
    const fetchData = async () => {
      const userInfoRequest = await getUserInfo();
      if ("username" in userInfoRequest) {
        setUsername(userInfoRequest.username);
      }
      else {
        navigate(`/login`)
      }
    };

    fetchData();
  }, [])

  const onPublish = async () => {
    const content = editorRef.current.getContent()
    const contentBytes = new TextEncoder().encode(content).length + title.length;
    const contentSizeInMegabytes = (contentBytes / 1024) / 1024;
    console.log(contentSizeInMegabytes)
    if (contentSizeInMegabytes <= 0) {
      return alert("Your blog post empty!")
    }
    else if (contentSizeInMegabytes > blogPostMaxSize) {
      return alert("Your blog post is too heavy! Try removing some of the images/media.")
    }
    else {
      const request = await postBlog(title, content)
      if (!("blog_id" in request)) {
        alert("An error occured, check the console!")
        return console.log(request.message)
      }
      const blogId = request.blog_id
      console.log(content)
      navigate(`/blogs/${username.replace(/\s+/g, '-')}/${blogId}`)
    }
  }

  return (
    <div className="personal-blog-write-container">
      <div className="title-publish-container">
        <input 
          type="text" 
          placeholder="Title" 
          className="post-title" 
          value={title} 
          onChange={(e) => setTitle(e.target.value)}
        />
        <button className="publish" type="submit" onClick={onPublish}>Publish</button>
      </div>
      <Editor
        onInit={(evt, editor) => editorRef.current = editor}
        tinymceScriptSrc={"/tinymce/tinymce.min.js"}
        initialValue=""
        init={{
          link_default_target: '_blank',
          autoresize_bottom_margin: 50,
          file_picker_callback: (cb, value, meta) => {
            const input = document.createElement('input');
            input.setAttribute('type', 'file');
            
            input.addEventListener('change', (e) => {
              const file = e.target.files[0];
              
              const reader = new FileReader();
              reader.addEventListener('load', () => {
                /*
                Note: Now we need to register the blob in TinyMCEs image blob
                registry. In the next release this part hopefully won't be
                necessary, as we are looking to handle it internally.
                */
              const id = 'blobid' + (new Date()).getTime();
              console.log(id)
              const blobCache =  tinymce.activeEditor.editorUpload.blobCache;
              console.log(blobCache)
              const base64 = reader.result.split(',')[1];
              console.log(base64)
              const blobInfo = blobCache.create(id, file, base64);
              console.log(blobInfo)
                blobCache.add(blobInfo);
                
                /* call the callback and populate the Title field with the file name */
                cb(blobInfo.blobUri(), { title: file.name });
              });
              reader.readAsDataURL(file);
              console.log(file.name)
            });
            
            input.click();
          },
          plugins: [
            "advlist", "autolink", "lists", "link", "image", "charmap",
            "anchor", "searchreplace", "visualblocks", "code", "insertdatetime",
            "media", "table", "help", "wordcount", "image", "autoresize",
            "quickbars"
          ],
          toolbar: "undo redo | blocks | bold italic forecolor | " +
          "alignleft aligncenter alignright alignjustify | " +
          "image media | " + 
          "bullist numlist outdent indent | " +
          "removeformat | help",
          content_style: "html { overflow-y: scroll; }"
        }}
        />
    </div>
  )
}

export default PersonalBlogWrite