import React from 'react'

import { push } from 'connected-react-router'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import { Row, Col } from 'react-bootstrap'

import {
  increment,
  incrementAsync,
  decrement,
  decrementAsync
} from '../../modules/counter'

import { fetchStationList } from '../../modules/station'

import StationList from './StationList'
import LoggerStatus from './LoggerStatus'

class Dashboard extends React.Component {
  render() {
    return (
      <div>
        <h1 className="app-heading">Radio Logger v5 GUI</h1>
        <Row>
          <Col>
            <StationList />
          </Col>
          <Col>
            <LoggerStatus />
            
          </Col>
        </Row>
      </div>
    )
  }
}

/*<p>Count: {props.count}</p>

            <p>
              <button onClick={props.increment}>Increment</button>
              <button onClick={props.incrementAsync} disabled={props.isIncrementing}>
                Increment Async
              </button>
            </p>

            <p>
              <button onClick={props.decrement}>Decrement</button>
              <button onClick={props.decrementAsync} disabled={props.isDecrementing}>
                Decrement Async
              </button>
            </p>

            <p>
              <button onClick={() => props.changePage()}>
                Go to about page via redux
              </button>
            </p>*/

const mapStateToProps = ({ counter, station }) => ({
  count: counter.count,
  stations: station.stations,
  isIncrementing: counter.isIncrementing,
  isDecrementing: counter.isDecrementing
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      increment,
      incrementAsync,
      decrement,
      decrementAsync,
      changePage: () => push('/about-us'),
      fetchStationList,
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Dashboard)
