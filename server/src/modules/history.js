import fetch from 'cross-fetch'
import { API_URL } from './'

export const ACQUIRE_STATION_HISTORY = 'history/ACQUIRE_STATION_HISTORY'
export const RECEIVE_STATION_HISTORY = 'history/RECEIVE_STATION_HISTORY'
export const RECEIVE_ERROR_STATION_HISTORY = 'history/RECEIVE_ERROR_STATION_HISTORY'

const initialState = {
  playHistory: {},
  lastUpdated: null,
  error: null,
  acquireInProgress: false,
  initialized: {},
}

// TODO: make all state independent of station/ separate by station id

export default (state = initialState, action) => {
  let output = null 

  switch (action.type) {

    case ACQUIRE_STATION_HISTORY:
      output = {
        ...state,
        error: null,
        acquireInProgress: true,
      }
      output['initialized'][action.station_id] = true

      return output

    case RECEIVE_STATION_HISTORY:
      output = {
        ...state,
        lastUpdated: action.payload._ts,
        acquireInProgress: false,
      }
      output['playHistory'][action.station_id] = action.payload.data

      return output

    case RECEIVE_ERROR_STATION_HISTORY:
      return {
        ...state,
        error: action.error,
        acquireInProgress: false,
      }

    default:
      return state
  }
}

const acquireStationHistory = (station_id) => {
  return {
    type: ACQUIRE_STATION_HISTORY,
    station_id
  }
}

const receiveStationHistory = (station_id, payload) => {
  return {
    type: RECEIVE_STATION_HISTORY,
    station_id,
    payload
  }
}

const receiveErrorStationHistory = (station_id, error) => {
  return {
    type: RECEIVE_ERROR_STATION_HISTORY,
    station_id,
    error: error
  }
}

export const fetchStationHistory = (station_id) => {
  return dispatch => {
    dispatch(acquireStationHistory(station_id))
    return fetch(`${API_URL}/station/${station_id}/history`, {
      headers: {
        'Authorization': 'Bearer asdf'
      }
    }).then(
      response => response.json().then(json => {
        if (json.status === 'ok')
          dispatch(receiveStationHistory(station_id, json))
        else {
          console.log('A server error occurred.', json)
          dispatch(receiveErrorStationHistory(station_id, json.error))
        }
      }),

      error => {
        console.log('An network error occurred.', error)
        dispatch(receiveErrorStationHistory(station_id, {
          type: 'Network Error',
          message: error,
          code: 1001
        }))
      }
    )
  }
} 

