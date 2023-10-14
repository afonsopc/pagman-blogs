import React from 'react'
import { Link } from 'react-router-dom'

const Footer = () => {
  return (
    <div className="footer-container">
        <p>
            Copyright © 2023 blogs.pagman.org. All rights reserved.
        </p>
        <p>
            <Link to="/">Home</Link> | <Link to="mailto:mail@pagman.org">Contact</Link> | <Link to="https://calc.pagman.org">Calculator</Link> | <Link to="https://passgen.pagman.org">Password Generator</Link>
        </p>
    </div>
  )
}

export default Footer