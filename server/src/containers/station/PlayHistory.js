import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { Table, Button } from 'react-bootstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import { fetchStationHistory } from '../../modules/history'

class PlayHistory extends React.Component {

  componentWillMount() {
    this.initializeHistory()
  }

  initializeHistory() {
    if (this.props.historyInit[this.props.station.id] !== true) {
      this.props.fetchStationHistory(this.props.station.id)
    }
    this.station_id = this.props.station.id
  }

  renderTable() {
    if (this.props.acquiring) return null;
    
    let tr = []
    const station_history = this.props.history[this.props.station.id]

    if (station_history === undefined) return null;

    station_history.map((history, key) => {
      return tr.push(
        <tr key={key} className={history.default ? 'table-danger' : ''}>
          <td>{history.ts}</td>
          <td>{history.artist}</td>
          <td>
            <Link to={`/station/${this.station_id}/track/${history.track_id}`}>{history.title}</Link>
          </td>
        </tr>
      )
    }) 

    return tr
  }

  render() {

    if (this.station_id !== this.props.station.id)
      this.initializeHistory()

    return (
      <div>
        <h1>Play History of {this.props.station.name}</h1>
        <Table bordered striped size="sm" hover>
          <thead>
            <tr>
              <td>Timestamp</td>
              <td>Artist</td>
              <td>Title</td>
            </tr>
          </thead>
          <tbody>
            { this.props.acquiring ? 
              <tr>
                <td colSpan={3} className="text-center text-muted">
                  <b><FontAwesomeIcon icon="spinner" spin /> Loading...</b>
                </td>
              </tr> : 
              this.renderTable() }
          </tbody>
        </Table>
        <div className="text-center footer-button">
          <Button variant="secondary" disabled={this.props.acquiring}>
            <FontAwesomeIcon icon="plus" /> Load More</Button>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ history }) => ({
  history: history.playHistory,
  acquiring: history.acquireInProgress,
  error: history.error,
  historyInit: history.initialized,
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    { fetchStationHistory },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(PlayHistory)