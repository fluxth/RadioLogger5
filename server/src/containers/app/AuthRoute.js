import React from 'react'

import { Redirect } from 'react-router'
import { Route } from 'react-router-dom'

import { connect } from 'react-redux'


const AuthRoute = ({ component: Component, ...rest }) => (
  <Route {...rest} render={(props) => (
    rest.isAuth === true ? 
      <Component {...props} /> : 
      <Redirect to={{ 
        pathname: '/auth/login',
        search: '?from=' + encodeURIComponent(props.location.pathname), 
        state: { redirect_from: props.location }
      }} />    
  )} />
);

const mapStateToProps = ({ auth }) => ({
  'isAuth': auth.authenticated
})

export default connect(mapStateToProps)(AuthRoute)