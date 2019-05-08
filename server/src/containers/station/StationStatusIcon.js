import React from 'react'

import { OverlayTrigger, Tooltip } from 'react-bootstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'


class StationStatusIcon extends React.Component {

  render() {
    const { station } = this.props
    let payload = ''
    let tooltipText = ''

    if (station.status === 'active') {
      payload = <FontAwesomeIcon icon="play-circle" className="text-success" />
      tooltipText = 'Active'

    } else if (station.status === 'stalled') {
      payload = <FontAwesomeIcon icon="exclamation-circle" className="text-warning" />
      tooltipText = 'Stalled'

    } else if (station.status === 'disabled') {
      payload = <FontAwesomeIcon icon="dot-circle" className="text-danger" />
      tooltipText = 'Disabled'

    } else {
      payload = <FontAwesomeIcon icon="dot-circle" />
      tooltipText = 'Status unknown'

    }

    return (
      <OverlayTrigger placement="left" overlay={
          <Tooltip id="tooltip-disabled">{tooltipText}</Tooltip>
        }>
        {payload}
      </OverlayTrigger>
    )
  }
}

export default StationStatusIcon