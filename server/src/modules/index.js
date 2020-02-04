import auth from './auth'
import stations from './stations'
import history from './station/history'

export const API_URL = 'http://127.0.0.1:5003/api'
// export const API_URL = '/api'
export const AUTH_STORAGE_KEY = 'authCredentials'

export default {
  auth,
  stations,
  history
}
