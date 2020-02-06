import React from 'react'

import { push } from 'connected-react-router'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import { Row, Col } from 'react-bootstrap'

import { setPageTitle } from '../../helpers'
import { fetchStationList } from '../../modules/stations'

import StationList from './StationList'
import LoggerStatus from './LoggerStatus'

class Dashboard extends React.Component {
  componentDidMount() {
    setPageTitle('Dashboard')
  }

  render() {
    return (
      <div>
        <h1 className="app-heading">Radio Logger v5 GUI</h1>
        <Row>
          <Col sm={12} md={8}>
            <StationList />
          </Col>
          <Col sm={12} md={4}>
            <LoggerStatus />
          </Col>
        </Row>
      </div>
    )
  }
}


const mapStateToProps = ({ stations }) => ({
  stations: stations.stations,
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      fetchStationList,
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Dashboard)
