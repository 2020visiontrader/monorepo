import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add organization and brand context to requests
api.interceptors.request.use((config) => {
  const orgId = localStorage.getItem('orgId');
  const brandId = localStorage.getItem('brandId');
  
  if (orgId) {
    config.headers['X-Organization-ID'] = orgId;
  }
  if (brandId) {
    config.headers['X-Brand-ID'] = brandId;
    // Add brand_id to query params if GET request
    if (config.method === 'get' && !config.params) {
      config.params = {};
    }
    if (config.method === 'get' && brandId) {
      config.params = { ...config.params, brand_id: brandId };
    }
  }
  
  return config;
});

// Auth endpoints
export const auth = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
};

// Content endpoints
export const content = {
  generate: (brandId: string, productIds: string[], fields: string[], variants: number) =>
    api.post('/content/generate', { brand_id: brandId, product_ids: productIds, fields, variants }),
  bulkAcceptVariants: (ids: string[]) =>
    api.post('/content/variants/bulk-accept', { ids }),
  bulkRejectVariants: (ids: string[]) =>
    api.post('/content/variants/bulk-reject', { ids }),
};

// Competitor endpoints
export const competitors = {
  recrawl: (id: string, opts?: { force?: boolean; max_pages?: number }) =>
    api.post(`/competitors/${id}/recrawl`, opts || {}),
};

// Job endpoints
export const jobs = {
  getLogs: (jobId: string, offset = 0, limit = 200) =>
    api.get(`/jobs/${jobId}/logs`, { params: { offset, limit } }),
};

// Template endpoints
export const templates = {
  applyVariant: (variantId: string) =>
    api.post(`/templates/variants/${variantId}/apply`),
};

// Brand endpoints
export const brands = {
  getProfile: (brandId: string) =>
    api.get(`/brands/${brandId}/profile`),
  updateProfile: (brandId: string, payload: any) =>
    api.put(`/brands/${brandId}/profile`, payload),
  getBlueprint: (brandId: string) =>
    api.get(`/brands/${brandId}/blueprint`),
  putBlueprint: (brandId: string, json: any) =>
    api.put(`/brands/${brandId}/blueprint`, { json }),
  mutateBlueprintSection: (brandId: string, action: string, sectionKey: string, index?: number, props?: any) =>
    api.post(`/brands/${brandId}/blueprint/sections`, { action, section_key: sectionKey, index, props }),
};

// Shopify endpoints
export const shopify = {
  getConnection: (brandId: string) =>
    api.get('/shopify/connection', { params: { brand_id: brandId } }),
  disconnect: (brandId: string) =>
    api.post('/shopify/disconnect', { brand_id: brandId }),
};

export default api;

