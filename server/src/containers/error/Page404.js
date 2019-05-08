import React from 'react'

import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const Page404 = ({ location }) => (
   <div className="jumbo-heading">
      <h1>
        <FontAwesomeIcon icon="exclamation-triangle" /> 404 Not Found
      </h1>
      <h3>The URL at <code>{location.pathname}</code> does not exist.</h3>
      <Link style={{ 'marginTop': '20px' }} className="btn btn-primary" to="/">
        <FontAwesomeIcon icon="chevron-left" /> Back to homepage
      </Link>
   </div>
)

export default Page404