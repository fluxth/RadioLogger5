import React from 'react'
import { Redirect } from 'react-router'
import { Route, Switch } from 'react-router-dom'

import { Container } from 'react-bootstrap'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { login } from '../../modules/auth'

import AuthRoute from './AuthRoute'
import { AUTH_STORAGE_KEY } from '../../modules'

import Dashboard from '../dashboard'
import Station from '../station'
import Login from '../login'
import AppNavbar from './AppNavbar'

import Page404 from '../error/Page404'

class App extends React.Component {

  constructor(props) {
    super(props)

    this.initialized = false
  }

  componentWillMount() {
    let auth = sessionStorage.getItem(AUTH_STORAGE_KEY)
    if (auth === null)
      auth = localStorage.getItem(AUTH_STORAGE_KEY)

    if (auth !== null) {
      auth = JSON.parse(auth)
      if ('accessToken' in auth && auth.accessToken.length > 0)
        this.props.login(auth)
      else
        this.initialized = true

    } else {
      this.initialized = true
    }
  }

  render() {

    if (this.props.isAuth && !this.initialized)
      this.initialized = true

    if (!this.initialized)
      return null

    return (
      <div>
        <AppNavbar />
        <Container id="mainContainer">
          <Switch>
            <Route exact path="/auth/login" component={Login} />
            <AuthRoute exact path="/" component={() => <Redirect to="/dashboard" />} />
            <AuthRoute exact path="/dashboard" component={Dashboard} />
            <AuthRoute exact path="/station/:id" component={Station} />
            <Route component={Page404} />
          </Switch>
        </Container>
      </div>
    )
  }
}

const mapStateToProps = ({ auth }) => ({
  isAuth: auth.authenticated
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      login
    },
    dispatch
  )

export default connect(mapStateToProps, mapDispatchToProps)(App)
