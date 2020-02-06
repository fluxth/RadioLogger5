import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { Table, Button } from 'react-bootstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import HumanizeDuration from 'humanize-duration'

import { history } from '../../store'
import { fetchStationHistory } from '../../modules/station/history'

import { findLast } from 'lodash'

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
      this.props.fetchStationHistory(this.props.station.id, {
        c: 100
      })
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

    const last_track = findLast(this.table_data, o => o.row_type === 'track')
    this.props.fetchStationHistory(this.props.station.id, {
      mod: 'old',
      id: last_track.data.id,
      c: 100
    })

    return false
  }

  buildTableData(station, station_history) {
    const table_data = []
    const play_history = station_history.playHistory

    if (play_history === undefined || play_history.length <= 0)
      return table_data

    const gap_min = 1000*60*7 // TODO: Move this to settings

    let prior_dt = null
    for (let key = play_history.length - 1; key >= 0; key--) {
      const history = play_history[key]

      let toth_done = false
      for (let i = 0; true; i++) {
      
        const now_dt = new Date()
        const dt = new Date(history.ts)

        const row_data = []

        // Ordinary tracks
        if (!toth_done) {
          const track_row = this.buildTrackTableRow({ station, history, key, dt })
          row_data.push(track_row)
        }

        // Gap and live gap detection
        const is_first = (key <= 0)
        if (prior_dt !== null || is_first) {
          let diff = 0
          if (is_first)
            diff = now_dt - dt
          else
            diff = dt - prior_dt

          if (diff > gap_min) {
            const gap_row = this.buildGapTableRow({ 
              key: key - 0.7 + (i/10), 
              dt: is_first ? now_dt : prior_dt, 
              diff, 
              live: is_first 
            })

            if (is_first)
              row_data.push(gap_row)
            else
              row_data.unshift(gap_row)
          }
        }

        // Top of the hour
        if (prior_dt !== null && !toth_done) {
          if (prior_dt.getHours() !== dt.getHours()) {
            const toth_dt = new Date(dt)
            toth_dt.setHours(toth_dt.getHours(), 0, 0)

            const toth_row = this.buildTothTableRow({ key: key - 0.3 + (i/10), dt: toth_dt })
            table_data.push(toth_row)

            prior_dt = dt
            dt = toth_dt

            toth_done = true
            continue
          }
        }

        table_data.push(...row_data)

        prior_dt = dt
        break
      }
    }
    
    return table_data.reverse()
  }

  buildTrackTableRow({ station, history, key, dt }) {
    return {
      row_type: 'track',
      play_type: history.default ? 'default_track' : 'track',
      color_class: history.default ? 'table-danger' : '',
      key,
      data: history,
      timestamp: {
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
      key,
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
      key,
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

  renderTable(table_data, station_history) {
    let tr = []

    // TODO: Move this to settings
    const ENABLED_PLAYTYPES = {
      'track': true,
      'default_track': true,
      'toth_marker': true,
      'gap_marker': true,
      'livegap_marker': true,
    }

    if (table_data !== undefined && table_data.length > 0) {
      table_data.map((table_item, key) => {

        if (!ENABLED_PLAYTYPES[table_item.play_type])
          return false
        
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

        return true
      })
    }

    if (station_history.acquireInProgress)
      return [
        ...tr,
        <tr key={-1}>
          <td colSpan={4} className="text-center text-muted">
            <b><FontAwesomeIcon icon="spinner" spin /> Loading...</b>
          </td>
        </tr>
      ]
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

      return true
    })

    return <div>{ option_items }</div>
  }

  render() {

    if (!this.isHistoryInitialized())
      return null

    const { station } = this.props
    const station_history = this.props.stationsHistory[station.id]

    this.table_data = this.buildTableData(station, station_history)

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
            { this.renderTable(this.table_data, station_history) }
          </tbody>
        </Table>
        <div className="text-center footer-button">
          <Button variant="secondary" disabled={station_history.acquireInProgress} onClick={this.loadMoreClick.bind(this)}>
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