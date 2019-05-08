import { API_URL, AUTH_STORAGE_KEY } from './'

export const ACQUIRE_TOKEN = 'auth/ACQUIRE_TOKEN'
export const RECEIVE_TOKEN = 'auth/RECEIVE_TOKEN'
export const RECEIVE_ERROR_TOKEN = 'auth/RECEIVE_ERROR_TOKEN'
export const LOGIN = 'auth/LOGIN'
export const LOGOUT = 'auth/LOGOUT'

const initialState = {
  authenticated: false,
  acquireInProgress: false,
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
        acquireInProgress: false,
      }

    case LOGIN:
      return {
        ...state,
        authenticated: true,
        userData: action.credentials
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
    return fetch(`${API_URL}/authenticate`).then(
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
        console.log('An network error occurred.', error)
        dispatch(receiveErrorToken({
          type: 'Network Error',
          message: error.message,
          code: 1001
        }))
      }
    )
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

export const logout = () => {
  return dispatch => {

    localStorage.removeItem(AUTH_STORAGE_KEY)
    sessionStorage.removeItem(AUTH_STORAGE_KEY)

    dispatch({
      type: LOGOUT
    })
  }
}