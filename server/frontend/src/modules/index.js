import auth from './auth'
import stations from './stations'
import history from './station/history'

export const API_URL = 'http://127.0.0.1:5003/api/v1'
// export const API_URL = '/api/v1'
export const AUTH_STORAGE_KEY = 'authCredentials'

export default {
  auth,
  stations,
  history
}
