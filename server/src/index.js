import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { ConnectedRouter } from 'connected-react-router'
import store, { history } from './store'
import App from './containers/app'

import 'sanitize.css/sanitize.css'
import 'bootstrap/dist/css/bootstrap.css'
import './index.css'

import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faTasks, faSatelliteDish, faClipboardList, faClipboardCheck, faUser, faUsers, faLock, faKey,
  faPlayCircle, faExclamationCircle, faDotCircle, faTimes,
  faSpinner, faSync,
  faChevronLeft, faExclamationTriangle, faPlus
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faTasks, faSatelliteDish, faClipboardList, faClipboardCheck, faUser, faUsers, faLock, faKey,
  faPlayCircle, faExclamationCircle, faDotCircle, faTimes,
  faSpinner, faSync,
  faChevronLeft, faExclamationTriangle, faPlus
)

const target = document.querySelector('#root')
const content = (
	<Provider store={store}>
	  <ConnectedRouter history={history}>
	    <div>
	      <App />
	    </div>
	  </ConnectedRouter>
	</Provider>
)

render(content, target)
