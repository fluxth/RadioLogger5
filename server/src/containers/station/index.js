import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import { find } from 'lodash'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import StationStatusIcon from '../station/StationStatusIcon'

import Page404 from '../error/Page404'
import PlayHistory from './PlayHistory'

import { fetchStationList } from '../../modules/station'


class Station extends React.Component {

  initializeStation() {
    this.station_id = this.props.match.params.id
    this.station = find(this.props.stations, (o) => {
      return o.id == this.station_id
    })
  }

  updateStation() {
    if (this.station === undefined || this.station_id !== this.props.match.params.id)
      this.initializeStation()
  }

  componentDidMount() {
    // check if station list exists
    // load logs

    if (!this.props.stationInit)
      this.props.fetchStationList()
  }

  render() {
    if (!this.props.stationInit || this.props.acquiring)
      return (
        <h2 className="jumbo-heading text-muted text-center">
          <FontAwesomeIcon icon="spinner" spin /> Loading...
        </h2>
      )

    this.updateStation()

    if (this.station === undefined)
      return <Page404 {...this.props} />

    return (
      <div>
        <h1>
          <StationStatusIcon station={this.station} /> {this.station.name}
        </h1>
        <hr />
        <PlayHistory station={this.station} />
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
)(Station)
