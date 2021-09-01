import axios from 'axios'

let $axios = axios.create({
  baseURL: '/api/',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// Request Interceptor
$axios.interceptors.request.use(function (config) {
  config.headers['Authorization'] = 'Fake Token'
  return config
})

// Response Interceptor to handle and log errors
$axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  // Handle Error
  console.log(error)
  return Promise.reject(error)
})

export default {

  fetchResource () {
    return $axios.get(`resource/xxx`)
      .then(response => response.data)
  },

  fetchSecureResource () {
    return $axios.get(`secure-resource/zzz`)
      .then(response => response.data)
  },

  fetchTrailInfo () {
    return $axios.get(`trail-info/yyy`)
      .then(response => response.data)
  },

  fetchLocation (location) {
    console.log('working', location)
    return $axios.get('get_location/', {
      params: {
        location: location
      }
    })
      .then(response => response.data)
  },

  runModel (text, miles, park, length, difficulty) {
    console.log('running model')
    return $axios.get('run_model/', {
      params: {
        text: text,
        miles: miles,
        park: park,
        length: length,
        difficulty: difficulty
      }
    })
      .then(response => response.data)
  }
}
