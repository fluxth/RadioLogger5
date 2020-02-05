import fetch from 'cross-fetch'
import { API_URL } from '.'

export const ACQUIRE_STATION_LIST = 'station/ACQUIRE_STATION_LIST'
export const RECEIVE_STATION_LIST = 'station/RECEIVE_STATION_LIST'
export const RECEIVE_ERROR_STATION_LIST = 'station/RECEIVE_ERROR_STATION_LIST'


const initialState = {
  stations: [],
  lastUpdated: null,
  error: null,
  acquireInProgress: false,
  initialized: false,
}

export default (state = initialState, action) => {
  switch (action.type) {

    case ACQUIRE_STATION_LIST:
      return {
        ...state,
        error: null,
        acquireInProgress: true,
        initialized: true,
      }

    case RECEIVE_STATION_LIST:
      return {
        ...state,
        stations: action.payload.data,
        lastUpdated: action.payload._ts,
        acquireInProgress: false,
      }

    case RECEIVE_ERROR_STATION_LIST:
      return {
        ...state,
        error: action.error,
        acquireInProgress: false,
      }

    default:
      return state
  }
}

const acquireStationList = () => {
  return {
    type: ACQUIRE_STATION_LIST
  }
}

const receiveStationList = (payload) => {
  return {
    type: RECEIVE_STATION_LIST,
    payload
  }
}

const receiveErrorStationList = (error) => {
  return {
    type: RECEIVE_ERROR_STATION_LIST,
    error: error,
    initialized: false
  }
}

export const fetchStationList = () => {
  return dispatch => {
    dispatch(acquireStationList())
    return fetch(`${API_URL}/stations`, {
      headers: {
        'Authorization': 'Bearer asdf'
      }
    }).then(
      response => response.json().then(json => {
        if (json.status === 'ok')
          dispatch(receiveStationList(json))
        else {
          console.log('A server error occurred.', json)
          dispatch(receiveErrorStationList(json.error))
        }
      }),

      error => {
        console.log('An network error occurred.', error)
        dispatch(receiveErrorStationList({
          type: 'Network Error',
          message: error.message,
          code: 1001
        }))
      }
    )
  }
} 
