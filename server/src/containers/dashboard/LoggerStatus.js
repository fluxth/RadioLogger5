import React from 'react'

import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import { Card } from 'react-bootstrap';

class LoggerStatus extends React.Component {
  render() {
    return (
      <Card>
        <Card.Body>
          <Card.Title>
            Logger Status
          </Card.Title>
          <Card.Subtitle className="mb-2 text-muted">Running version 5.0.1</Card.Subtitle>
          <Card.Text>
            Information not available
          </Card.Text>
          <Card.Link href="#">Reload</Card.Link>
          <Card.Link href="#" variant="danger">Shutdown</Card.Link>
        </Card.Body>
      </Card>
    )
  }
}

const mapStateToProps = ({  }) => ({

})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {  },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(LoggerStatus)
