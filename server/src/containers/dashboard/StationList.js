import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { Table, Alert, Button } from 'react-bootstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import StationStatusIcon from '../station/StationStatusIcon'

import { format } from 'timeago.js'

import { fetchStationList } from '../../modules/station'


class StationList extends React.Component {

  componentWillMount() {
    if (!this.props.stationInit)
      this.props.fetchStationList()
  }

  renderTable() {
    if (this.props.acquiring) return null;

    let tr = []
    this.props.stations.map((station, key) => {

      return tr.push(
        <tr key={key}>
          <td>
            <StationStatusIcon station={station} />&nbsp;
            <Link to={'/station/' + station.id}>{station.name}</Link>
          </td>
          <td>{format(station.last_play)}</td>
          <td>{station.tracks}</td>
        </tr>
      )
    }) 

    return tr
  }

  renderErrorAlert() {
    const { error } = this.props
    return (
      <Alert variant="danger">
        <Alert.Heading>{ error.type } [{error.code}]</Alert.Heading>
        <p>
          Station List could not load: <b>{ error.message }</b><br />
        </p>
        <hr />
        <div className="d-flex justify-content-end">
          <Button onClick={this.props.fetchStationList} variant="outline-danger">
            <FontAwesomeIcon icon="sync" /> Retry
          </Button>
        </div>
      </Alert>
    )
  }

  render() {
    const { props } = this

    if (props.error !== null)
      return this.renderErrorAlert()

    return (
      <div>
        <Table bordered hover>
          <thead>
            <tr>
              <td>Station</td>
              <td>Last Play</td>
              <td>Tracks</td>
            </tr>
          </thead>
          <tbody>
           { this.props.acquiring ? 
              <tr>
                <td colSpan={3} className="text-center text-muted">
                  <b><FontAwesomeIcon icon="spinner" spin /> Loading...</b>
                </td>
              </tr> 
              : this.renderTable() }
          </tbody>
        </Table>
      </div>
    )
  }
}

const mapStateToProps = ({ station }) => ({
  stations: station.stations,
  acquiring: station.acquireInProgress,
  error: station.error,
  stationInit: station.initialized,
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    { fetchStationList },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(StationList)
