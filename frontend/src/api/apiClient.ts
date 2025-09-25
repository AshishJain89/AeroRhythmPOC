import axios, { AxiosResponse, AxiosError } from 'axios';

/* -------------------------------
   Types
   ------------------------------- */
export interface AuthToken { access_token: string; token_type: string; }

export interface ApiError { message: string; code?: string; status?: number; details?: any; }


/* -------------------------------
   Config
   ------------------------------- */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';

/* -------------------------------
   Axios instance
   ------------------------------- */
// export const apiClient = axios.create({
//   baseURL: BASE_URL, 
//   timeout: 10000, 
//   headers: { 'Content-Type': 'application/json', }, 
//   withCredentials: true,
// });
export const apiClient = axios.create({
  baseURL: '${import.meta.env.VITE_API_BASE_URL}/api/v1',
  withCredentials: true,
})

apiClient.interceptors.response.use(
  (response) => response, 
  (error) => {
    console.error("API error:", error?.response?.status, error?.message);
    return Promise.reject(error);
  }
);

/* -------------------------------
   Request interceptor (auth)
   ------------------------------- */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) { config.headers.Authorization = `Bearer ${token}`; }
    return config;
  },
  (error) => Promise.reject(error)
);


/* -------------------------------
   Response interceptor (errors)
   Consolidated single interceptor to normalize errors
   ------------------------------- */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: error.message || 'An unexpected error occurred',
      status: error.response?.status,
      details: error.response?.data,
    };

    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }

    console.error("API error:", apiError);
    return Promise.reject(apiError);
  }
);

/* -------------------------------
   Generic apiRequest helper
   Usage: apiRequest(() => apiClient.get('/api/xxx'))
   Returns: Promise<T>
   ------------------------------- */
export const apiRequest = async <T>( requestFn: () => Promise<AxiosResponse<T>> ): Promise<T> => {
  if (USE_MOCK_DATA) {
    // This is a developer-only feature.
    // It is not intended for production use.
    console.warn( 'VITE_USE_MOCK_DATA is enabled. This should not be used in production.' );
  }
  const response = await requestFn();
  return response.data;
};

/* -------------------------------
   Small mock datasets (dev only)
   Replace / expand these with realistic mock fixtures as needed.
   ------------------------------- */
const mock = {
  user: { id: 1, name: "Demo User", role: "crew_scheduler" },
  crews: [
    { id: "CPT001", name: "Rajesh Kumar", base: "DEL", role: "CPT" },
    { id: "FO002", name: "Anita Sharma", base: "BOM", role: "FO" },
  ],
  flights: [
    { id: "F100", from: "DEL", to: "BOM", dep: "09:00", arr: "10:30" },
    { id: "F101", from: "BOM", to: "DEL", dep: "12:00", arr: "13:30" },
  ],
  disruptions: [
    { id: "D1", flightId: "F100", type: "weather", severity: "medium", note: "Thunderstorm" },
  ],
  rosters: [
    { id: "R1", crewId: "CPT001", flightId: "F100", dutyStart: "2025-09-01T08:00:00Z" },
  ],
};

/* -------------------------------
   API endpoint wrappers
   Exported functions that components/query hooks use
   They return mock data when USE_MOCK_DATA=true
   ------------------------------- */
export const api = {
  getUser: async () => {
    if (USE_MOCK_DATA) return Promise.resolve(mock.user);
    return apiRequest(() => apiClient.get("/auth/me"));
  },

  getCrews: async () => {
    if (USE_MOCK_DATA) return Promise.resolve(mock.crews);
    return apiRequest(() => apiClient.get("/crews/"));
  },

  getFlights: async () => {
    if (USE_MOCK_DATA) return Promise.resolve(mock.flights);
    return apiRequest(() => apiClient.get("/flights/"));
  },

  getDisruptions: async () => {
    if (USE_MOCK_DATA) return Promise.resolve(mock.disruptions);
    return apiRequest(() => apiClient.get("/disruptions/"));
  },

  getRosters: async (start: string, end: string) => {
    if (USE_MOCK_DATA) return Promise.resolve(mock.rosters);
    return apiRequest(() => 
      apiClient.get("/rosters/", { params: {start, end } })
    );
  },

  createDisruption: async (payload: any) => {
    if (USE_MOCK_DATA) {
      return Promise.resolve({ id: `D-mock-${Date.now()}`, ...payload });
    }
    return apiRequest(() => apiClient.post("/disruptions/", payload));
  },

  // add more wrappers here as your UI needs them...
};

/* -------------------------------
   Auth helpers (kept from your file)
   ------------------------------- */
export const setAuthToken = (token: string) => {
  localStorage.setItem('auth_token', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const removeAuthToken = () => {
  localStorage.removeItem('auth_token');
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

export default apiClient;
