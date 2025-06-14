import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// 请求拦截器：添加认证信息
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理错误
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (!error.response) {
      console.error('网络错误，无法连接到服务器');
      return Promise.reject({ message: '网络错误，请检查您的网络连接或服务器是否运行' });
    }

    if (error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject({ message: '登录已过期，请重新登录' });
    }
    
    return Promise.reject(error.response.data || { message: '请求失败' });
  }
);

export default apiClient; 