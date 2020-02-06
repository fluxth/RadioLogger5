import { API_URL, AUTH_STORAGE_KEY } from './'

export const ACQUIRE_TOKEN = 'auth/ACQUIRE_TOKEN'
export const RECEIVE_TOKEN = 'auth/RECEIVE_TOKEN'
export const RECEIVE_ERROR_TOKEN = 'auth/RECEIVE_ERROR_TOKEN'
export const DISMISS_ALERT = 'auth/DISMISS_ALERT'
export const LOGIN = 'auth/LOGIN'
export const LOGOUT = 'auth/LOGOUT'

const initialState = {
  authenticated: false,
  acquireInProgress: false,
  authAlert: false,
  authAlertData: {
    variant: null,
    payload: null,
  },
  userData: {
    accessToken: null,
    username: null,
  }
}

export default (state = initialState, action) => {
  switch (action.type) {
    case ACQUIRE_TOKEN:
      return {
        ...state,
        authAlert: false,
        authAlertData: initialState['authAlertData'],
        acquireInProgress: true,
      }

    case RECEIVE_TOKEN:
      return {
        ...state,
        acquireInProgress: false,
      }

    case RECEIVE_ERROR_TOKEN:
      return {
        ...state,
        authAlert: true,
        authAlertData: {
          variant: 'danger',
          payload: action.error,
        },
        acquireInProgress: false,
      }

    case DISMISS_ALERT:
      return {
        ...state,
        authAlert: false,
      }

    case LOGIN:
      return {
        ...state,
        authenticated: true,
        userData: {
          ...action.credentials,
          expires: new Date(action.credentials.expires * 1000)
        }
      }

    case LOGOUT:
      return {
        ...state,
        authenticated: false,
        userData: initialState['userData'],
      }

    default:
      return state
  }
}

export const attemptLogin = (username, password, remember) => {
  return dispatch => {
    dispatch(acquireToken())
    return fetch(`${API_URL}/authenticate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify({
        username,
        password,
        remember
      })
    }).then(
      response => response.json().then(json => {
        if (json.status === 'ok') {
          dispatch(receiveToken())
          dispatch(login(json.data))

          let storage = null
          if (remember === true)
            storage = localStorage
          else
            storage = sessionStorage

          storage.setItem(AUTH_STORAGE_KEY, JSON.stringify(json.data))
          
        } else {
          console.log('A server error occurred.', json)
          dispatch(receiveErrorToken(json.error))
        }
      }),

      error => {
        console.log('A network error occurred.', error)
        dispatch(receiveErrorToken({
          type: 'Network Error',
          message: error.message,
          code: 1001
        }))
      }
    ).catch((error) => {
      console.log(error)
      dispatch(receiveErrorToken({
        type: 'Unexpected Error',
        message: error.message,
        code: 1901
      }))
    })
  }
} 

const acquireToken = () => {
  return {
    type: ACQUIRE_TOKEN
  }
}

const receiveToken = () => {
  return {
    type: RECEIVE_TOKEN
  }
}

const receiveErrorToken = (error) => {
  return {
    type: RECEIVE_ERROR_TOKEN,
    error: error
  }
}

export const login = (creds) => {
  return dispatch => {
    dispatch({
      type: LOGIN,
      credentials: creds
    })
  }
}

export const dismissAlert = () => {
  return {
    type: DISMISS_ALERT
  }
}

export const logout = () => {
  return dispatch => {

    localStorage.removeItem(AUTH_STORAGE_KEY)
    sessionStorage.removeItem(AUTH_STORAGE_KEY)

    dispatch({
      type: LOGOUT
    })
  }
}