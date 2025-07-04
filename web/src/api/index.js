import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://172.20.10.3:5000/api',
  timeout: 5000
})

instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default instance 