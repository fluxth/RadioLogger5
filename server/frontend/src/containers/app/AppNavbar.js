import React from 'react'
import { withRouter } from 'react-router'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { login, logout } from '../../modules/auth'

import { Navbar, Nav, NavDropdown, Dropdown } from 'react-bootstrap'
import { LinkContainer } from 'react-router-bootstrap'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import StationStatusIcon from '../station/StationStatusIcon'

import { fetchStationList } from '../../modules/stations'


class AppNavbar extends React.Component {

  componentDidMount() {
    setTimeout(() => {
      const { stationInit, auth } = this.props
      if (!stationInit && auth.authenticated) {
        this.props.fetchStationList()
      }
    }, 500)
  }

  logoutClick = () => {
    this.props.logout()
  }

  renderStationListDropdown = () => {

    if (this.props.acquiring) 
      return <Dropdown.Header>Loading stations...</Dropdown.Header>

    if (this.props.stations.length <= 0)
      return (<Dropdown.Header>
        <FontAwesomeIcon icon="times" /> Stations not loaded
      </Dropdown.Header>)

    const list = []

    this.props.stations.map((station, key) => {
      return list.push(
        <LinkContainer to={ '/station/' + station.id } key={key}>
          <NavDropdown.Item>
            <StationStatusIcon station={station} /> { station.name }
          </NavDropdown.Item>
        </LinkContainer>
      )
    })

    return list
  }


  render() {
    const loggedInNav = (
      <Navbar.Collapse id="responsive-navbar-nav">
        <Nav className="mr-auto">
          <LinkContainer to="/dashboard">
            <Nav.Link>
              <FontAwesomeIcon icon="tasks" /> Dashboard
            </Nav.Link>
          </LinkContainer>
          <NavDropdown title={
            <span>
              <FontAwesomeIcon icon="satellite-dish" /> Stations
            </span>
          } id="stations-nav-dropdown" active={ this.props.location.pathname.startsWith('/station/') }>
          
            { this.renderStationListDropdown() }

          </NavDropdown>
          <LinkContainer to="/status">
            <Nav.Link>
              <FontAwesomeIcon icon="clipboard-check" /> Status
            </Nav.Link>
          </LinkContainer>
          <LinkContainer to="/logs">
            <Nav.Link>
              <FontAwesomeIcon icon="clipboard-list" /> Logs
            </Nav.Link>
          </LinkContainer>
        </Nav>
        <Nav>
          <NavDropdown title={
            <span>
              <FontAwesomeIcon icon="user" /> { this.props.auth.userData.username }
            </span>
          } alignRight id="account-nav-dropdown">
            <LinkContainer to="/settings">
              <NavDropdown.Item>
                <FontAwesomeIcon icon="cog" /> Settings
              </NavDropdown.Item>
            </LinkContainer>
            <LinkContainer to="/profile">
              <NavDropdown.Item>
                <FontAwesomeIcon icon="user" /> Edit Profile
              </NavDropdown.Item>
            </LinkContainer>
            <LinkContainer to="/users">
              <NavDropdown.Item>
                <FontAwesomeIcon icon="users" /> Manage Users
              </NavDropdown.Item>
            </LinkContainer>
            <NavDropdown.Divider />
            <NavDropdown.Item onClick={this.logoutClick}>
              <FontAwesomeIcon icon="key" /> Log out
            </NavDropdown.Item>
          </NavDropdown>
        </Nav>
      </Navbar.Collapse>
    )

    const loggedOutNav = (
      <Navbar.Collapse id="responsive-navbar-nav">
        <Nav className="ml-auto">
          <LinkContainer to="/auth/login">
            <Nav.Link>
              <FontAwesomeIcon icon="lock" /> Login
            </Nav.Link>
          </LinkContainer>
        </Nav>
      </Navbar.Collapse>
    )

    return (
      <Navbar bg="dark" variant="dark" sticky="top" expand="sm">
        <LinkContainer to="/">
          <Navbar.Brand>RL5 GUI</Navbar.Brand>
        </LinkContainer>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        { this.props.auth.authenticated ? loggedInNav : loggedOutNav }
      </Navbar>
    )
  }
}

const mapStateToProps = ({ auth, stations }) => ({
  auth: auth,

  stations: stations.stations,
  acquiring: stations.acquireInProgress,
  error: stations.error,
  stationInit: stations.initialized,
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      login,
      logout,
      fetchStationList
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(withRouter(AppNavbar))