import React from 'react'
import { Link } from 'react-router-dom'

const minimalNavbar = () => {
  return (
    <div className="minimal-navbar-container">
      <Link to="/" className="back-button">←</Link>
    </div>
  )
}

export default minimalNavbar