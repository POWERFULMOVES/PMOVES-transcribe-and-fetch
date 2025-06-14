import { BACKEND_URL as API_BASE_URL } from '@/lib/constants';

const apiClient = {
  async get(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'GET',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
    }
    return response.json();
  },

  async post(path, data, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
    }
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        return response.json();
    }
    return response.text();
  },

  // You can add other methods like put, delete, patch as needed
  // Example for PUT:
  // async put(url, data, options = {}) {
  //   const response = await fetch(url, {
  //     method: 'PUT',
  //     ...options,
  //     headers: {
  //       'Content-Type': 'application/json',
  //       ...(options.headers || {}),
  //     },
  //     body: JSON.stringify(data),
  //   });
  //   if (!response.ok) {
  //     const errorData = await response.json().catch(() => ({ message: response.statusText }));
  //     throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
  //   }
  //   return response.json();
  // },
};

export default apiClient; 