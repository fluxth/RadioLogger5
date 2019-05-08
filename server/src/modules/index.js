import counter from './counter'
import auth from './auth'
import station from './station'
import history from './history'

export const API_URL = 'http://127.0.0.1:5000/api'
// export const API_URL = '/api'
export const AUTH_STORAGE_KEY = 'authCredentials'

export default {
  counter,
  auth,
  station,
  history
}
