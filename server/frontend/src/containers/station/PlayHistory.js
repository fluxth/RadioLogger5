import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { Table, Button } from 'react-bootstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import HumanizeDuration from 'humanize-duration'

import { history } from '../../store'
import { fetchStationHistory } from '../../modules/station/history'

class PlayHistory extends React.Component {

  componentDidMount() {
    this.history_unlisten = history.listen((location, action) => {
      this.initializeHistory()
    });

    this.initializeHistory()
  }

  componentWillUnmount() {
    this.history_unlisten();
  }

  isHistoryInitialized() {
    const { station, stationsHistory } = this.props

    if (!(station.id in stationsHistory))
      return false
    else if (stationsHistory[station.id].initialized !== true)
      return false
    return true
  }

  initializeHistory() {
    if (!this.isHistoryInitialized())
      this.props.fetchStationHistory(this.props.station.id)
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

  buildTableData(station, station_history) {
    const table_data = []
    const play_history = station_history.playHistory

    const gap_min = 1000*60*7 // TODO: Move this to settings

    let prior_dt = null
    play_history.map((history, key) => {
    
      const now_dt = new Date()
      const dt = new Date(history.ts)

      // Top of the hour
      if (prior_dt !== null) {
        if (prior_dt.getHours() !== dt.getHours()) {
          const toth_dt = new Date(dt)
          toth_dt.setHours(toth_dt.getHours() + 1, 0, 0)

          const toth_row = this.buildTothTableRow({ key, dt: toth_dt })
          table_data.push(toth_row)

          prior_dt = toth_dt
        }
      }

      // Gap and live gap detection
      const is_first = (key <= 0)
      if (prior_dt !== null || is_first) {
        let diff = 0
        if (is_first)
          diff = now_dt - dt
        else
          diff = prior_dt - dt

        if (diff > gap_min) {
          const gap_row = this.buildGapTableRow({ key, dt, diff, live: is_first })
          table_data.push(gap_row)
        }
      }

      const track_row = this.buildTrackTableRow({ station, history, key, dt })
      table_data.push(track_row)

      prior_dt = dt
    })
    
    return table_data
  }

  buildTrackTableRow({ station, history, key, dt }) {
    return {
      row_type: 'track',
      play_type: history.default ? 'default_track' : 'track',
      color_class: history.default ? 'table-danger' : '',
      key: key,
      timestamp: {
        data: dt,
        text: this.formatTimestamp(dt),
        href: null,
      },
      artist: {
        text: history.artist,
        href: history.default ? null : '/station/' + station.id + '/artist?name=' + encodeURIComponent(history.artist),
      },
      title: {
        text: history.title,
        href: '/track/' + history.track_id,
      },
      options: []
    }
  }

  buildTothTableRow({ key, dt }) {
    return {
      row_type: 'marker',
      play_type: 'toth_marker',
      color_class: 'table-success',
      key: key - 0.5,
      timestamp: {
        data: dt,
        text: this.formatTimestamp(dt),
        href: null,
      },
      marker: {
        text: [
          'TOP OF THE HOUR - ' + dt.getHours() + ':00'
        ]
      },
      options: []
    }
  }

  buildGapTableRow({ key, dt, diff, live }) {
    return {
      row_type: 'track_marker',
      play_type: (live) ? 'livegap_marker' : 'gap_marker',
      color_class: 'table-secondary',
      key: key - 0.2,
      timestamp: {
        data: dt,
        text: this.formatTimestamp(dt),
        href: null,
      },
      marker: {
        text: [
          (live) ? 'LIVE GAP' : 'GAP',
          HumanizeDuration(diff, { 
            units: ['d', 'h', 'm'], 
            round: true 
          })
        ]
      },
      options: []
    }
  }

  renderTable(table_data) {
    let tr = []

    // TODO: Move this to settings
    const ENABLED_PLAYTYPES = {
      'track': true,
      'default_track': true,
      'toth_marker': true,
      'gap_marker': true,
      'livegap_marker': true,
    }

    if (table_data === undefined || table_data.length <= 0)
      return null

    table_data.map((table_item, key) => {

      if (!ENABLED_PLAYTYPES[table_item.play_type])
        return
      
      // Row type = track
      if (['track'].includes(table_item.row_type)) {
        tr.push(
          <tr key={table_item.key} className={table_item.color_class}>
            <td>{table_item.timestamp.text}</td>
            <td>{table_item.artist.href === null ?
                  table_item.artist.text :
                  <Link to={table_item.artist.href}>
                    {table_item.artist.text}
                  </Link>
                }
            </td>
            <td>{table_item.title.href === null ?
                  table_item.title.text :
                  <Link to={table_item.title.href}>
                    {table_item.title.text}
                  </Link>
                }
            </td>
            <td>
              { this.renderTableRowOptions(table_item.options) }
            </td>
          </tr>
        )
      }
      
      // Row type = options_marker
      else if (['marker', 'options_marker'].includes(table_item.row_type)) {
        tr.push(
          <tr key={table_item.key} className={table_item.color_class}>
            <td>{table_item.timestamp.text}</td>
            <td colSpan={2} className="text-center">
              {table_item.marker.text[0]}
            </td>
            <td>
              { this.renderTableRowOptions(table_item.options) }
            </td>
          </tr>
        )
      }

      // Row type = track_marker
      else if (['track_marker'].includes(table_item.row_type)) {
        tr.push(
          <tr key={table_item.key} className={table_item.color_class}>
            <td>{table_item.timestamp.text}</td>
            <td className="text-center">
              {table_item.marker.text[0]}
            </td>
            <td className="text-center">
              {table_item.marker.text[1]}
            </td>
            <td>
              { this.renderTableRowOptions(table_item.options) }
            </td>
          </tr>
        )
      }

    })

    return tr
  }

  renderTableRowOptions(options) {
    const option_items = []

    options.map((option, key) => {

      // Button
      if (option.type === 'button') {
        const obj = (
          <Button key={key} {...option.props}>
            {option.text}
          </Button>
        )
        option_items.push(obj)
      }

      // Link
      if (option.type === 'link') {
        const obj = (
          <Link key={key} {...option.props}>
            {option.text}
          </Link>
        )
        option_items.push(obj)
      }

    })

    return <div>{ option_items }</div>
  }

  render() {

    if (!this.isHistoryInitialized())
      return null

    const { station } = this.props
    const station_history = this.props.stationsHistory[station.id]

    let table_body
    if (station_history.acquireInProgress)
      table_body = (
        <tr>
          <td colSpan={4} className="text-center text-muted">
            <b><FontAwesomeIcon icon="spinner" spin /> Loading...</b>
          </td>
        </tr>
      )
    else
      table_body = this.renderTable(this.buildTableData(station, station_history))
    
    return (
      <div>
        <h1>Play History of {station.name}</h1>
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
            { table_body }
          </tbody>
        </Table>
        <div className="text-center footer-button">
          <Button variant="secondary" disabled={station_history.acquireInProgress} onClick={this.loadMoreClick}>
            <FontAwesomeIcon icon="plus" /> Load More</Button>
        </div>
      </div>
    )
  }
}

const mapStateToProps = ({ history }) => ({
  stationsHistory: history.stations,
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