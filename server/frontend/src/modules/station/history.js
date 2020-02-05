import fetch from 'cross-fetch'
import qs from 'query-string'
import { API_URL } from '..'

export const ACQUIRE_STATION_HISTORY = 'history/ACQUIRE_STATION_HISTORY'
export const RECEIVE_CLEAR_STATION_HISTORY = 'history/RECEIVE_CLEAR_STATION_HISTORY'
export const RECEIVE_APPEND_STATION_HISTORY = 'history/RECEIVE_APPEND_STATION_HISTORY'
export const RECEIVE_PREPEND_STATION_HISTORY = 'history/RECEIVE_PREPEND_STATION_HISTORY'
export const RECEIVE_ERROR_STATION_HISTORY = 'history/RECEIVE_ERROR_STATION_HISTORY'

const initialState = {
  stations: {
    // 0: {
    //   playHistory: [],
    //   lastUpdated: null,
    //   error: null,
    //   acquireInProgress: false,
    //   initialized: false,
    // }
  }
}

export default (state = initialState, action) => {
  switch (action.type) {

    case ACQUIRE_STATION_HISTORY:
      return { 
        ...state,
        stations: {
          ...state.stations,
          [action.station_id]: {
            ...state.stations[action.station_id],
            error: null,
            acquireInProgress: true,
            initialized: true
          }
        }  
      }

    case RECEIVE_CLEAR_STATION_HISTORY:
      return {
        ...state,
        stations: {
          ...state.stations,
          [action.station_id]: {
            ...state.stations[action.station_id],
            lastUpdated: new Date(action.payload._ts * 1000),
            acquireInProgress: false,
            playHistory: action.payload.data
          }
        }
      }

    case RECEIVE_APPEND_STATION_HISTORY:
      return {
        ...state,
        stations: {
          ...state.stations,
          [action.station_id]: {
            ...state.stations[action.station_id],
            lastUpdated: new Date(action.payload._ts * 1000),
            acquireInProgress: false,
            playHistory: [
              ...state.stations[action.station_id].playHistory,
              ...action.payload.data
            ]
          }
        }
      }

    case RECEIVE_PREPEND_STATION_HISTORY:
      return {
        ...state,
        stations: {
          ...state.stations,
          [action.station_id]: {
            ...state.stations[action.station_id],
            lastUpdated: new Date(action.payload._ts * 1000),
            acquireInProgress: false,
            playHistory: [
              ...action.payload.data,
              ...state.stations[action.station_id].playHistory
            ]
          }
        }
      }

    case RECEIVE_ERROR_STATION_HISTORY:
      return {
        ...state,
        stations: {
          ...state.stations,
          [action.station_id]: {
            ...state.stations[action.station_id],
            error: action.error,
            acquireInProgress: false,
          }
        }
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

const receiveClearStationHistory = (station_id, payload) => {
  return {
    type: RECEIVE_CLEAR_STATION_HISTORY,
    station_id,
    payload
  }
}

const receiveAppendStationHistory = (station_id, payload) => {
  return {
    type: RECEIVE_APPEND_STATION_HISTORY,
    station_id,
    payload
  }
}

const receivePrependStationHistory = (station_id, payload) => {
  return {
    type: RECEIVE_PREPEND_STATION_HISTORY,
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

export const fetchStationHistory = (station_id, options = null) => {
  return dispatch => {
    dispatch(acquireStationHistory(station_id))

    let query = ''
    if (options !== null) {
      query = '?' + qs.stringify({ ...options })
    }

    return fetch(`${API_URL}/station/${station_id}/history${query}`, {
      headers: {
        'Authorization': 'Bearer asdf'
      }
    }).then(
      response => response.json().then(json => {
        if (json.status === 'ok') {
          if (json.action === 'clear')
            dispatch(receiveClearStationHistory(station_id, json))
          else if (json.action === 'append')
            dispatch(receiveAppendStationHistory(station_id, json))
          else if (json.action === 'prepend')
            dispatch(receivePrependStationHistory(station_id, json))
        }
        else {
          console.log('A server error occurred.', json)
          dispatch(receiveErrorStationHistory(station_id, json.error))
        }
      }),

      error => {
        console.log('A network error occurred.', error)
        dispatch(receiveErrorStationHistory(station_id, {
          type: 'Network Error',
          message: error,
          code: 1001
        }))
      }
    ).catch((error) => {
      console.log(error)
      dispatch(receiveErrorStationHistory(station_id, {
        type: 'Unexpected Error',
        message: error.message,
        code: 1901
      }))
    })
  }
} 

