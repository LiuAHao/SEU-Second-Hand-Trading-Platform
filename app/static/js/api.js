/**
 * ============================================
 * SEU 校园二手交易平台 - 前端 API 接口层
 * 企业级接口设计规范
 * ============================================
 * 
 * 功能：
 * - 统一管理所有后端 API 请求
 * - 提供请求拦截和响应处理
 * - 实现错误处理和重试机制
 * - 提供类型检查和参数验证
 */

/**
 * API 配置
 */
const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 10000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000,
};

/**
 * 错误类型定义
 */
const ERROR_TYPES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

/**
 * HTTP 状态码处理映射
 */
const STATUS_CODE_MAP = {
  400: { type: ERROR_TYPES.VALIDATION_ERROR, message: '请求参数错误' },
  401: { type: ERROR_TYPES.AUTH_ERROR, message: '未授权，请登录' },
  403: { type: ERROR_TYPES.AUTH_ERROR, message: '禁止访问' },
  404: { type: ERROR_TYPES.SERVER_ERROR, message: '资源不存在' },
  405: { type: ERROR_TYPES.VALIDATION_ERROR, message: '请求方法不被允许' },
  500: { type: ERROR_TYPES.SERVER_ERROR, message: '服务器内部错误' },
  503: { type: ERROR_TYPES.SERVER_ERROR, message: '服务暂时不可用' },
};

/**
 * API 请求类
 */
class APIClient {
  constructor(config = {}) {
    this.baseURL = config.baseURL || API_CONFIG.BASE_URL;
    this.timeout = config.timeout || API_CONFIG.TIMEOUT;
    this.retryTimes = config.retryTimes || API_CONFIG.RETRY_TIMES;
    this.retryDelay = config.retryDelay || API_CONFIG.RETRY_DELAY;
    this.interceptors = {
      request: [],
      response: [],
      error: [],
    };
  }

  /**
   * 添加请求拦截器
   * @param {Function} callback - 拦截回调函数
   */
  addRequestInterceptor(callback) {
    this.interceptors.request.push(callback);
  }

  /**
   * 添加响应拦截器
   * @param {Function} callback - 拦截回调函数
   */
  addResponseInterceptor(callback) {
    this.interceptors.response.push(callback);
  }

  /**
   * 添加错误拦截器
   * @param {Function} callback - 错误拦截回调函数
   */
  addErrorInterceptor(callback) {
    this.interceptors.error.push(callback);
  }

  /**
   * 执行请求拦截器
   * @private
   */
  async executeRequestInterceptors(config) {
    let modifiedConfig = { ...config };
    for (const interceptor of this.interceptors.request) {
      modifiedConfig = await interceptor(modifiedConfig);
    }
    return modifiedConfig;
  }

  /**
   * 执行响应拦截器
   * @private
   */
  async executeResponseInterceptors(response) {
    let modifiedResponse = { ...response };
    for (const interceptor of this.interceptors.response) {
      modifiedResponse = await interceptor(modifiedResponse);
    }
    return modifiedResponse;
  }

  /**
   * 执行错误拦截器
   * @private
   */
  async executeErrorInterceptors(error) {
    let modifiedError = { ...error };
    for (const interceptor of this.interceptors.error) {
      modifiedError = await interceptor(modifiedError);
    }
    return modifiedError;
  }

  /**
   * 检查响应数据结构
   * @private
   */
  validateResponse(response) {
    if (!response || typeof response !== 'object') {
      throw {
        type: ERROR_TYPES.SERVER_ERROR,
        message: '无效的响应格式',
        statusCode: 0,
      };
    }
    return response;
  }

  /**
   * 处理 HTTP 错误
   * @private
   */
  handleHTTPError(statusCode, data) {
    const errorInfo = STATUS_CODE_MAP[statusCode] || {
      type: ERROR_TYPES.SERVER_ERROR,
      message: `HTTP Error ${statusCode}`,
    };

    const serverMessage = (data && (data.message || data.error || data.msg)) || '';
    const message = serverMessage || errorInfo.message;

    return {
      ...errorInfo,
      message,
      statusCode,
      data,
    };
  }

  /**
   * 创建超时 Promise
   * @private
   */
  createTimeoutPromise() {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject({
          type: ERROR_TYPES.TIMEOUT_ERROR,
          message: '请求超时',
        });
      }, this.timeout);
    });
  }

  /**
   * 发送 HTTP 请求（带重试机制）
   * @private
   */
  async request(method, url, data = null, retries = 0) {
    try {
      // 构建请求配置
      let config = {
        method,
        url: `${this.baseURL}${url}`,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(data);
      }

      // 执行请求拦截器
      config = await this.executeRequestInterceptors(config);

      // 设置超时
      const fetchPromise = fetch(config.url, {
        method: config.method,
        headers: config.headers,
        body: config.body,
      });

      const response = await Promise.race([
        fetchPromise,
        this.createTimeoutPromise(),
      ]);

      // 检查 HTTP 状态
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const error = this.handleHTTPError(response.status, data);
        throw error;
      }

      // 解析响应
      const responseData = await response.json();
      const validatedData = this.validateResponse(responseData);

      // 执行响应拦截器
      const finalData = await this.executeResponseInterceptors(validatedData);

      return finalData;
    } catch (error) {
      // 检查是否需要重试
      if (
        retries < this.retryTimes &&
        (error.type === ERROR_TYPES.NETWORK_ERROR ||
         error.type === ERROR_TYPES.TIMEOUT_ERROR)
      ) {
        await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        return this.request(method, url, data, retries + 1);
      }

      // 执行错误拦截器
      const handledError = await this.executeErrorInterceptors(error);
      throw handledError;
    }
  }

  /**
   * GET 请求
   */
  async get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request('GET', fullUrl);
  }

  /**
   * POST 请求
   */
  async post(url, data) {
    return this.request('POST', url, data);
  }

  /**
   * PUT 请求
   */
  async put(url, data) {
    return this.request('PUT', url, data);
  }

  /**
   * PATCH 请求
   */
  async patch(url, data) {
    return this.request('PATCH', url, data);
  }

  /**
   * DELETE 请求
   */
  async delete(url) {
    return this.request('DELETE', url);
  }

  /**
   * 上传文件（FormData）
   */
  async upload(url, formData) {
    try {
      let config = {
        method: 'POST',
        url: `${this.baseURL}${url}`,
        headers: {},
        body: formData,
      };

      // 执行请求拦截器（可注入 Token）
      config = await this.executeRequestInterceptors(config);

      const response = await fetch(config.url, {
        method: config.method,
        headers: config.headers,
        body: config.body,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const error = this.handleHTTPError(response.status, data);
        throw error;
      }

      const responseData = await response.json();
      const validatedData = this.validateResponse(responseData);
      const finalData = await this.executeResponseInterceptors(validatedData);
      return finalData;
    } catch (error) {
      const handledError = await this.executeErrorInterceptors(error);
      throw handledError;
    }
  }
}

/**
 * 创建全局 API 客户端实例
 */
const apiClient = new APIClient();

/**
 * 添加请求拦截器 - 自动注入 Token
 */
apiClient.addRequestInterceptor(async (config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

/**
 * ============================================
 * 用户相关 API
 * ============================================
 */
const userAPI = {
  /**
   * 用户注册
   * @param {Object} userData - 用户数据
   * @param {string} userData.username - 用户名
   * @param {string} userData.password - 密码
   * @param {string} userData.email - 邮箱
   * @returns {Promise}
   */
  register: (userData) => apiClient.post('/user/register', userData),

  /**
   * 用户登录
   * @param {Object} credentials - 登录凭证
   * @param {string} credentials.username - 用户名
   * @param {string} credentials.password - 密码
   * @returns {Promise}
   */
  login: (credentials) => apiClient.post('/user/login', credentials),

  /**
   * 用户登出
   * @returns {Promise}
   */
  logout: () => apiClient.post('/user/logout', {}),

  /**
   * 获取当前登录用户信息
   * @returns {Promise}
   */
  getCurrentUser: () => apiClient.get('/user/getCurrentUser'),

  /**
   * 获取用户资料
   * @param {number|string} userId - 用户ID
   * @returns {Promise}
   */
  getUserProfile: (userId) => apiClient.get(`/user/getUserProfile/${userId}`),

  /**
   * 更新用户资料
   * @param {Object} userData - 更新的用户数据
   * @returns {Promise}
   */
  updateProfile: (userData) => apiClient.post('/user/updateProfile', userData),

  /**
   * 检查用户名是否可用
   * @param {string} username - 用户名
   * @returns {Promise}
   */
  checkUsername: (username) => apiClient.get(`/user/checkUsername/${username}`),

  /**
   * 检查邮箱是否已注册
   * @param {string} email - 邮箱
   * @returns {Promise}
   */
  checkEmail: (email) => apiClient.get(`/user/checkEmail/${email}`),
};

/**
 * ============================================
 * 商品相关 API
 * ============================================
 */
const itemAPI = {
  /**
   * 获取首页推荐商品
   * @param {Object} options - 查询选项
   * @param {number} options.limit - 限制数量
   * @returns {Promise}
   */
  getFeatured: (options = {}) =>
    apiClient.post('/item/getFeatured', { limit: options.limit || 12 }),

  /**
   * 搜索商品
   * @param {Object} params - 搜索参数
   * @param {string} params.query - 搜索关键词
   * @param {string} params.type - 搜索类型 (title|seller|category)
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.category - 分类过滤
   * @param {number} params.minPrice - 最小价格
   * @param {number} params.maxPrice - 最大价格
   * @param {string} params.sort - 排序字段
   * @returns {Promise}
   */
  search: (params) => apiClient.post('/item/search', params),

  /**
   * 按分类获取商品
   * @param {string} category - 分类名称
   * @param {Object} options - 查询选项
   * @returns {Promise}
   */
  getByCategory: (category, options = {}) =>
    apiClient.post('/item/getByCategory', { category, ...options }),

  /**
   * 获取单个商品详情
   * @param {number|string} itemId - 商品ID
   * @returns {Promise}
   */
  getDetail: (itemId) => apiClient.get(`/item/getDetail/${itemId}`),

  /**
   * 发布新商品
   * @param {Object} itemData - 商品数据
   * @param {string} itemData.title - 商品标题
   * @param {string} itemData.description - 商品描述
   * @param {number} itemData.price - 价格
   * @param {number} itemData.stock - 库存
   * @param {string} itemData.category - 分类
   * @param {Array} itemData.images - 图片URL数组
   * @returns {Promise}
   */
  create: (itemData) => apiClient.post('/item/create', itemData),

  /**
   * 更新商品
   * @param {number|string} itemId - 商品ID
   * @param {Object} itemData - 更新的数据
   * @returns {Promise}
   */
  update: (itemId, itemData) => apiClient.post(`/item/update/${itemId}`, itemData),

  /**
   * 删除商品
   * @param {number|string} itemId - 商品ID
   * @returns {Promise}
   */
  delete: (itemId) => apiClient.post(`/item/delete/${itemId}`, {}),

  /**
   * 获取用户发布的商品
   * @param {number|string} userId - 用户ID
   * @param {Object} options - 查询选项
   * @returns {Promise}
   */
  getUserItems: (userId, options = {}) =>
    apiClient.post('/item/search', { seller_id: userId, sort: 'latest', limit: options.limit || 12, page: options.page || 1 }),

  /**
   * 检查商品库存
   * @param {Object} items - 商品数组
   * @param {number} items[].itemId - 商品ID
   * @param {number} items[].quantity - 所需数量
   * @returns {Promise}
   */
  checkStock: (items) => apiClient.post('/items/check-stock', { items }),
};

/**
 * ============================================
 * 购物车相关 API
 * ============================================
 */
const cartAPI = {
  /**
   * 获取购物车内容
   * @returns {Promise}
   */
  getCart: () => apiClient.get('/cart'),

  /**
   * 添加商品到购物车
   * @param {Object} item - 商品信息
   * @param {number} item.itemId - 商品ID
   * @param {number} item.quantity - 数量
   * @returns {Promise}
   */
  addItem: (item) => apiClient.post('/cart/add', item),

  /**
   * 更新购物车商品数量
   * @param {number} itemId - 商品ID
   * @param {number} quantity - 新数量
   * @returns {Promise}
   */
  updateItem: (itemId, quantity) =>
    apiClient.post(`/cart/update/${itemId}`, { quantity }),

  /**
   * 移除购物车商品
   * @param {number} itemId - 商品ID
   * @returns {Promise}
   */
  removeItem: (itemId) => apiClient.post(`/cart/remove/${itemId}`, {}),

  /**
   * 清空购物车
   * @returns {Promise}
   */
  clear: () => apiClient.post('/cart/clear', {}),

  /**
   * 获取购物车统计信息
   * @returns {Promise}
   */
  getStats: () => apiClient.get('/cart/stats'),
};

/**
 * ============================================
 * 订单相关 API
 * ============================================
 */
const orderAPI = {
  /**
   * 创建订单（结账）
   * @param {Object} orderData - 订单数据
   * @param {Array} orderData.items - 订单项目
   * @param {string} orderData.deliveryAddress - 配送地址
   * @param {string} orderData.paymentMethod - 支付方式
   * @param {Object} orderData.paymentInfo - 支付信息
   * @returns {Promise}
   */
  create: (orderData) => apiClient.post('/orders', orderData),

  /**
   * 获取用户订单列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.status - 订单状态过滤
   * @returns {Promise}
   */
  getUserOrders: (params) => apiClient.get('/orders', params),

  /**
   * 获取订单详情
   * @param {number|string} orderId - 订单ID
   * @returns {Promise}
   */
  getDetail: (orderId) => apiClient.get(`/orders/${orderId}`),

  /**
   * 取消订单
   * @param {number|string} orderId - 订单ID
   * @returns {Promise}
   */
  cancel: (orderId) => apiClient.delete(`/orders/${orderId}`),

  /**
   * 获取订单支付二维码
   * @param {number|string} orderId - 订单ID
   * @returns {Promise}
   */
  getPaymentQR: (orderId) => apiClient.get(`/orders/${orderId}/payment-qr`),

  /**
   * 确认收货
   * @param {number|string} orderId - 订单ID
   * @returns {Promise}
   */
  confirmReceived: (orderId) => apiClient.post(`/orders/${orderId}/confirm`, {}),

  /**
   * 评价订单
   * @param {number|string} orderId - 订单ID
   * @param {Object} reviewData - 评价数据
   * @param {number} reviewData.rating - 评分
   * @param {string} reviewData.comment - 评论
   * @returns {Promise}
   */
  review: (orderId, reviewData) => 
    apiClient.post(`/orders/${orderId}/review`, reviewData),
};

/**
 * ============================================
 * 分类相关 API
 * ============================================
 */
const categoryAPI = {
  /**
   * 获取所有分类
   * @returns {Promise}
   */
  getAll: () => apiClient.get('/categories'),

  /**
   * 获取分类详情
   * @param {number|string} categoryId - 分类ID
   * @returns {Promise}
   */
  getDetail: (categoryId) => apiClient.get(`/categories/${categoryId}`),
};

/**
 * ============================================
 * 搜索/推荐相关 API
 * ============================================
 */
const recommendAPI = {
  /**
   * 获取热门商品（使用商品API）
   * @param {Object} options - 查询选项
   * @returns {Promise}
   */
  getPopular: (options = {}) =>
    apiClient.get('/item/getFeatured', { limit: options.limit || 12 }),

  /**
   * 获取最新商品（使用商品搜索API）
   * @param {Object} options - 查询选项
   * @returns {Promise}
   */
  getLatest: (options = {}) =>
    apiClient.post('/item/search', {
      sort: 'created_at_desc',
      limit: options.limit || 12
    }),

  /**
   * 获取用户个性化推荐（使用商品搜索API）
   * @param {Object} options - 查询选项
   * @returns {Promise}
   */
  getPersonalized: (options = {}) =>
    apiClient.post('/item/search', {
      sort: 'popular',
      limit: options.limit || 12
    }),

  /**
   * 获取搜索建议
   * @param {string} query - 搜索词
   * @returns {Promise}
   */
  getSearchSuggestions: (query) =>
    apiClient.get('/search/suggestions', { q: query }),
};

/**
 * ============================================
 * 地址相关 API
 * ============================================
 */
const addressAPI = {
  /**
   * 获取用户地址列表
   * @returns {Promise}
   */
  getList: () => apiClient.get('/addresses'),

  /**
   * 新增地址
   * @param {Object} addressData - 地址数据
   * @returns {Promise}
   */
  add: (addressData) => apiClient.post('/addresses', addressData),

  /**
   * 更新地址
   * @param {number|string} addressId - 地址ID
   * @param {Object} addressData - 地址数据
   * @returns {Promise}
   */
  update: (addressId, addressData) =>
    apiClient.put(`/addresses/${addressId}`, addressData),

  /**
   * 删除地址
   * @param {number|string} addressId - 地址ID
   * @returns {Promise}
   */
  delete: (addressId) => apiClient.delete(`/addresses/${addressId}`),

  /**
   * 设置默认地址
   * @param {number|string} addressId - 地址ID
   * @returns {Promise}
   */
  setDefault: (addressId) => apiClient.post(`/addresses/${addressId}/default`, {}),
};

/**
 * ============================================
 * 上传相关 API
 * ============================================
 */
const uploadAPI = {
  uploadImage: (file, type = 'item') => {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('type', type);
    return apiClient.upload('/upload/image', fd);
  },
};

/**
 * ============================================
 * API 导出对象
 * ============================================
 */
const API = {
  user: userAPI,
  item: itemAPI,
  cart: cartAPI,
  order: orderAPI,
  category: categoryAPI,
  recommend: recommendAPI,
  address: addressAPI,
   upload: uploadAPI,
  client: apiClient,
  ERROR_TYPES,
};

/**
 * 全局错误处理示例配置
 * 可在应用初始化时调用此函数来设置统一的错误处理
 */
function setupAPIErrorHandling() {
  // 添加全局错误拦截器
  apiClient.addErrorInterceptor((error) => {
    // 处理 401 未授权错误
    if (error.type === ERROR_TYPES.AUTH_ERROR && error.statusCode === 401) {
      // 清除本地用户信息
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      // 重定向到登录页
      window.location.href = '/login';
    }
    return error;
  });
}

// 导出 API 和工具函数
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API, setupAPIErrorHandling, APIClient };
} else {
  window.API = API;
  window.setupAPIErrorHandling = setupAPIErrorHandling;
  window.APIClient = APIClient;
}
