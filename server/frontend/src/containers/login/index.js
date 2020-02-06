import React from 'react'
import { Redirect } from 'react-router'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Form, Button, Row, Col, Alert, Modal } from 'react-bootstrap'

import { setPageTitle } from '../../helpers'
import { attemptLogin, dismissAlert } from '../../modules/auth'

import { has } from 'lodash'

// const { redirect_from } = this.props.location.state


class Login extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      'username': '',
      'password': '',
      'remember': true,
      'modalShown': false,
    }

    this.login = this.login.bind(this)
    this.handleInputChange = this.handleInputChange.bind(this)

  }

  handleModalClose = () => this.setState({ modalShown: false });
  handleModalShow = () => this.setState({ modalShown: true });

  componentDidMount() {
    setPageTitle('Login')
  }

  login(e) {
    e.preventDefault()

    this.props.attemptLogin(
      this.state.username,
      this.state.password,
      this.state.remember
    )
  }

  handleInputChange(e) {
    const target = e.target
    const value = target.type === 'checkbox' ? target.checked : target.value
    const name = target.name

    this.setState({
      [name]: value
    })
  }

  renderAlert() {
    const { variant, payload } = this.props.alertData
    return (
      <Alert variant={variant} dismissible onClose={this.props.dismissAlert.bind(this)}>
        <Alert.Heading>{payload.type} [{payload.code}]</Alert.Heading>
        {payload.message}, please try again later.
      </Alert>
    )
  }

  render() {

    if (this.props.isAuth === true) {
      if (has(this.props.location, 'state.redirect_from.pathname')) {
        return <Redirect to={ this.props.location.state.redirect_from.pathname } />
      }

      return <Redirect to="/dashboard" />
    }

    const dt = new Date()

    return (
      <Row className="justify-content-sm-center">
        <Modal show={this.state.modalShown} onHide={this.handleModalClose}>
          <Modal.Header closeButton>
            <Modal.Title>First time using RL5 GUI?</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>You can acquire your credentials to access this web GUI via the <code>RLManage</code> tool in your RadioLogger5 directory.</p>
            <p><i>But how?</i></p>
            <p>
              Simply launch your terminal and use the following command to create an admin user:<br />
              <code>./rlmanage.py user create-admin</code>
            </p>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={this.handleModalClose}>
              Thanks!
            </Button>
          </Modal.Footer>
        </Modal>
        <Col sm={10} md={6}>
          <h1 className="text-center mt-2 mb-4">Login</h1>
          <Form onSubmit={this.login}>
            { (this.props.showAlert === true) ? this.renderAlert() : '' }
            <Form.Group as={Row} controlId="formHorizontalUsername">
              <Form.Label className="text-right d-none d-sm-block" column sm={2}>
                <FontAwesomeIcon icon="user" />
              </Form.Label>
              <Col sm={10}>
                <Form.Control 
                  type="text" 
                  name="username"
                  value={this.state.username} 
                  onChange={this.handleInputChange} 
                  placeholder="Username"
                  required
                  disabled={this.props.loggingIn} />
              </Col>
            </Form.Group>

            <Form.Group as={Row} controlId="formHorizontalPassword">
              <Form.Label className="text-right d-none d-sm-block" column sm={2}>
                <FontAwesomeIcon icon="lock" />
              </Form.Label>
              <Col sm={10}>
                <Form.Control 
                  type="password" 
                  name="password"
                  value={this.state.password} 
                  onChange={this.handleInputChange} 
                  placeholder="Password"
                  required
                  disabled={this.props.loggingIn} />
              </Col>
            </Form.Group>

            <Form.Group as={Row} controlId="formHorizontalCheck">
              <Col sm={{ span: 10, offset: 2 }}>
                <Form.Check 
                  name="remember"
                  checked={this.state.remember}
                  onChange={this.handleInputChange} 
                  label="Remember me on this browser"
                  disabled={this.props.loggingIn} />
              </Col>
            </Form.Group>

            <Form.Group as={Row}>
              <Col sm={{ span: 10, offset: 2 }}>
                { 
                  this.props.loggingIn ? 
                    <Button type="submit" disabled={true}>
                      <FontAwesomeIcon icon="spinner" spin /> Logging in...
                    </Button> : 
                    <Button type="submit">
                      <FontAwesomeIcon icon="key" /> Log in
                    </Button>
                }
                
              </Col>
            </Form.Group>
          </Form>
          <div className="login-footer">
            <p className="text-center links">
              <Button variant="link" onClick={this.handleModalShow}>Don't know your credentials?</Button>
            </p>
            <hr />
            <p className="text-muted text-center">
                &copy; 2018-{ dt.getFullYear() }, All rights reserved.<br />
                Developed by fluxdev
            </p>
          </div>
        </Col>
      </Row>
    )
  }
}

const mapStateToProps = ({ auth }) => ({
  isAuth: auth.authenticated,
  loggingIn: auth.acquireInProgress,
  showAlert: auth.authAlert,
  alertData: auth.authAlertData,
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      attemptLogin,
      dismissAlert
    },
    dispatch
  )

export default connect(mapStateToProps, mapDispatchToProps)(Login)
