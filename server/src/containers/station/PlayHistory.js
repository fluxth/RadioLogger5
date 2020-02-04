import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { Table, Button } from 'react-bootstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import HumanizeDuration from 'humanize-duration'

import { fetchStationHistory } from '../../modules/station/history'

class PlayHistory extends React.Component {

  componentDidMount() {
    this.initializeHistory()
  }

  initializeHistory() {
    if (this.props.historyInit[this.props.station.id] !== true) {
      this.props.fetchStationHistory(this.props.station.id)
    }
    this.station_id = this.props.station.id
  }

  // TODO: Move this to a helper class
  formatTimestamp(dt) {
    return dt.toLocaleDateString(undefined, {
      weekday: 'short', month: 'short', day: 'numeric'
    }) + ' at ' +
    dt.toLocaleTimeString(undefined, {
      timeStyle: 'short',
      hour12: false
    })
  }

  loadMoreClick(e) {
    e.preventDefault()
    return false
  }

  renderTable() {
    if (this.props.acquiring) return null;
    
    let tr = []
    const station_history = this.props.history[this.props.station.id]

    if (station_history === undefined) return null;

    const gap_min = 1000*60*7
    const dt_now = new Date()

    let prior_dt = null
    let first = true
    station_history.map((history, key) => {
      const dt = new Date(history.ts)

      if (prior_dt !== null || first === true) {
        let diff = 0

        if (first === true)
          diff = dt_now - dt
        else
          diff = prior_dt - dt

        if (diff > gap_min) {
          tr.push(
            <tr key={key + 0.3} className="table-secondary">
              <td>{this.formatTimestamp(dt)}</td>
              <td className="text-center">
                { (first) ? 'LIVE ': '' }GAP
              </td>
              <td className="text-center">
                {HumanizeDuration(diff, { 
                  units: ['d', 'h', 'm'], 
                  round: true 
                })}
              </td>
              <td></td>
            </tr>
          )
        }

        if (first === true)
          first = false
      }

      if (prior_dt !== null) {
        if (prior_dt.getHours() !== dt.getHours()) {
          tr.push(
            <tr key={key + 0.5} className="table-success">
              <td>{this.formatTimestamp(dt)}</td>
              <td colSpan={2} className="text-center">
                TOP OF THE HOUR - {prior_dt.getHours()}:00
              </td>
              <td></td>
            </tr>
          )
        }
      }

      prior_dt = dt

      return tr.push(
        <tr key={key} className={history.default ? 'table-danger' : ''}>
          <td>{this.formatTimestamp(dt)}</td>
          <td>{history.artist}</td>
          <td>
            <Link to={`/track/${history.track_id}`}>{history.title}</Link>
          </td>
          <td></td>
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
              <td>Options</td>
            </tr>
          </thead>
          <tbody>
            { this.props.acquiring ? 
              <tr>
                <td colSpan={4} className="text-center text-muted">
                  <b><FontAwesomeIcon icon="spinner" spin /> Loading...</b>
                </td>
              </tr> : 
              this.renderTable() }
          </tbody>
        </Table>
        <div className="text-center footer-button">
          <Button variant="secondary" disabled={this.props.acquiring} onClick={this.loadMoreClick}>
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