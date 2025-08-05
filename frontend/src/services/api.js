import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.error || 'Sunucu hatası');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Sunucuya bağlanılamadı. Backend çalışıyor mu?');
    } else {
      // Something else happened
      throw new Error('Beklenmeyen hata oluştu');
    }
  }
);

export const apiService = {
  // System health check
  checkHealth: () => apiClient.get('/health'),
  
  // Table statistics
  getTableStats: () => apiClient.get('/tables/stats'),
  
  // Get brands
  getBrands: () => apiClient.get('/brands'),
  
  // Get sales data for dashboard
  getSalesData: () => apiClient.get('/dashboard/sales-data'),
  
  // Product search
  searchProducts: (query, filters = {}, limit = 10) => 
    apiClient.post('/search', { query, filters, limit }),
  
  // Product details
  getProductDetails: (productId, sourceTable) => 
    apiClient.get(`/product/${productId}/details?source_table=${sourceTable}`),
  
  // AI analysis
  analyzeProduct: (productId, sourceTable, query = 'Bu ürün için risk analizi yap') =>
    apiClient.post('/ai/analyze', { product_id: productId, source_table: sourceTable, query }),
  
  // AI chat
  chatWithAI: (message) => 
    apiClient.post('/ai/chat', { message }),
  
  // Create embeddings
  createEmbeddings: () => 
    apiClient.post('/embeddings/create'),
  
  // Test services
  testServices: () => 
    apiClient.get('/test'),
};

export default apiService;