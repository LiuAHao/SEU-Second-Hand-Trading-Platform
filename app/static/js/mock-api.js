/**
 * ============================================
 * 前端 Mock API - 用于测试和演示
 * 无需后端即可测试所有前端功能
 * ============================================
 * 
 * 使用方法：
 * 1. 在 base.html 中优先加载此文件
 * 2. 设置 window.USE_MOCK_API = true
 * 3. 所有 API 调用将被拦截并返回模拟数据
 */

/**
 * 模拟用户数据库
 */
const mockUsers = {
  'admin@seu.edu.cn': {
    id: 1,
    username: 'admin',
    email: 'admin@seu.edu.cn',
    name: '管理员',
    avatar: 'https://via.placeholder.com/100',
    phone: '13800138000',
    joinDate: '2024-01-01',
  },
  'test@seu.edu.cn': {
    id: 2,
    username: 'testuser',
    email: 'test@seu.edu.cn',
    name: '测试用户',
    avatar: 'https://via.placeholder.com/100',
    phone: '13800138001',
    joinDate: '2024-02-01',
  },
};

/**
 * 模拟商品数据库
 */
const mockItems = [
  {
    id: 1,
    title: 'MacBook Pro 2023',
    description: '全新MacBook Pro 15英寸，M3芯片，99新',
    price: 8999,
    originalPrice: 12999,
    stock: 2,
    images: ['https://via.placeholder.com/400x300?text=MacBook+Pro'],
    category: 'electronics',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.8,
    reviews: 12,
    createdAt: '2024-12-20',
  },
  {
    id: 2,
    title: '高数教科书',
    description: '高等数学第七版，有笔记，无损伤',
    price: 25,
    originalPrice: 45,
    stock: 5,
    images: ['https://via.placeholder.com/400x300?text=Math+Book'],
    category: 'books',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.5,
    reviews: 3,
    createdAt: '2024-12-19',
  },
  {
    id: 3,
    title: 'AirPods Pro',
    description: '苹果AirPods Pro，无损伤，充电完美',
    price: 1500,
    originalPrice: 1999,
    stock: 3,
    images: ['https://via.placeholder.com/400x300?text=AirPods+Pro'],
    category: 'electronics',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.9,
    reviews: 25,
    createdAt: '2024-12-18',
  },
  {
    id: 4,
    title: '自行车',
    description: '山地自行车，几乎全新，配件完整',
    price: 800,
    originalPrice: 1500,
    stock: 1,
    images: ['https://via.placeholder.com/400x300?text=Bicycle'],
    category: 'sports',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.6,
    reviews: 8,
    createdAt: '2024-12-17',
  },
  {
    id: 5,
    title: '羽毛球拍',
    description: '高级碳纤维羽毛球拍，轻便耐用',
    price: 300,
    originalPrice: 500,
    stock: 4,
    images: ['https://via.placeholder.com/400x300?text=Badminton'],
    category: 'sports',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.7,
    reviews: 15,
    createdAt: '2024-12-16',
  },
  {
    id: 6,
    title: 'Kindle Paperwhite',
    description: '第11代，8GB，含原装保护壳，电池健康',
    price: 520,
    originalPrice: 980,
    stock: 6,
    images: ['https://via.placeholder.com/400x300?text=Kindle'],
    category: 'electronics',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.6,
    reviews: 18,
    createdAt: '2024-12-15',
  },
  {
    id: 7,
    title: '宿舍小冰箱',
    description: '美的 90L 双门小冰箱，静音节能，送货到寝室',
    price: 480,
    originalPrice: 899,
    stock: 2,
    images: ['https://via.placeholder.com/400x300?text=Mini+Fridge'],
    category: 'furniture',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.4,
    reviews: 9,
    createdAt: '2024-12-14',
  },
  {
    id: 8,
    title: '考研政治笔记全套',
    description: '亲笔整理逐章框架+真题标注，赠思维导图 PDF',
    price: 120,
    originalPrice: 0,
    stock: 10,
    images: ['https://via.placeholder.com/400x300?text=Study+Notes'],
    category: 'books',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.9,
    reviews: 34,
    createdAt: '2024-12-13',
  },
  {
    id: 9,
    title: '篮球鞋 Nike Kyrie',
    description: '42码，九成新，室内木地板使用，包邮校内自提',
    price: 360,
    originalPrice: 899,
    stock: 3,
    images: ['https://via.placeholder.com/400x300?text=Basketball+Shoes'],
    category: 'sports',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.5,
    reviews: 11,
    createdAt: '2024-12-12',
  },
  {
    id: 10,
    title: '显示器 27 寸 2K',
    description: 'IPS 2K 75Hz，带支架和HDMI线，屏幕无亮点',
    price: 680,
    originalPrice: 1299,
    stock: 5,
    images: ['https://via.placeholder.com/400x300?text=Monitor+27'],
    category: 'electronics',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.7,
    reviews: 20,
    createdAt: '2024-12-11',
  },
  {
    id: 11,
    title: '蓝牙键盘鼠标套装',
    description: '支持多设备切换，含静音鼠标，适合平板/笔记本',
    price: 150,
    originalPrice: 299,
    stock: 12,
    images: ['https://via.placeholder.com/400x300?text=Keyboard+Mouse'],
    category: 'electronics',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.3,
    reviews: 7,
    createdAt: '2024-12-10',
  },
  {
    id: 12,
    title: '宿舍收纳柜',
    description: '四层抽屉塑料收纳柜，稳固无异味，含防尘罩',
    price: 90,
    originalPrice: 169,
    stock: 8,
    images: ['https://via.placeholder.com/400x300?text=Storage+Cabinet'],
    category: 'furniture',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.2,
    reviews: 5,
    createdAt: '2024-12-09',
  },
  {
    id: 13,
    title: '平板支架',
    description: '铝合金可折叠，支撑稳固，支持11英寸内平板',
    price: 45,
    originalPrice: 89,
    stock: 15,
    images: ['https://via.placeholder.com/400x300?text=Tablet+Stand'],
    category: 'electronics',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.1,
    reviews: 6,
    createdAt: '2024-12-08',
  },
  {
    id: 14,
    title: '考研数学真题',
    description: '数学二 2005-2024真题套装，附视频解析链接',
    price: 88,
    originalPrice: 0,
    stock: 20,
    images: ['https://via.placeholder.com/400x300?text=Math+Papers'],
    category: 'books',
    seller: mockUsers['test@seu.edu.cn'],
    rating: 4.8,
    reviews: 16,
    createdAt: '2024-12-07',
  },
  {
    id: 15,
    title: '插线板+Type-C快充',
    description: '6位插孔+2C1A，支持 65W PD，带过载保护',
    price: 110,
    originalPrice: 159,
    stock: 9,
    images: ['https://via.placeholder.com/400x300?text=Power+Strip'],
    category: 'other',
    seller: mockUsers['admin@seu.edu.cn'],
    rating: 4.6,
    reviews: 13,
    createdAt: '2024-12-06',
  },
];

/**
 * 模拟分类
 */
const mockCategories = [
  { id: 'electronics', name: '电子产品', icon: '📱' },
  { id: 'books', name: '书籍', icon: '📚' },
  { id: 'clothing', name: '服装', icon: '👕' },
  { id: 'sports', name: '运动', icon: '⚽' },
  { id: 'furniture', name: '家具', icon: '🛋️' },
  { id: 'other', name: '其他', icon: '📦' },
];

/**
 * 模拟 API 响应延迟（毫秒）
 */
const MOCK_DELAY = 500;

/**
 * 延迟响应
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Mock API 拦截器
 */
class MockAPIInterceptor {
  /**
   * 拦截 API 请求
   */
  static async intercept(endpoint, method, data) {
    await delay(MOCK_DELAY);

    console.log(`[Mock API] ${method.toUpperCase()} ${endpoint}`, data);

    // 用户相关
    if (endpoint === '/users/register' && method === 'post') {
      return MockAPIInterceptor.handleRegister(data);
    }
    if (endpoint === '/users/login' && method === 'post') {
      return MockAPIInterceptor.handleLogin(data);
    }
    if (endpoint === '/users/current' && method === 'get') {
      return MockAPIInterceptor.handleGetCurrentUser();
    }
    if (endpoint.startsWith('/users/') && method === 'get') {
      return MockAPIInterceptor.handleGetUser(endpoint);
    }

    // 商品相关
    if ((endpoint === '/items/search' && method === 'get') || (endpoint === '/item/search' && method === 'post')) {
      return MockAPIInterceptor.handleSearchItems(data);
    }
    if (endpoint.startsWith('/items/') && method === 'get') {
      return MockAPIInterceptor.handleGetItem(endpoint);
    }
    if (endpoint.startsWith('/item/getDetail/') && method === 'get') {
      return MockAPIInterceptor.handleGetItem(endpoint.replace('/item/getDetail', '/items'));
    }
    if (endpoint === '/items' && method === 'get') {
      return MockAPIInterceptor.handleGetItems(data);
    }
    if (endpoint === '/item/getFeatured' && method === 'get') {
      return MockAPIInterceptor.handleGetFeatured(data);
    }

    // 分类相关
    if (endpoint === '/categories' && method === 'get') {
      return MockAPIInterceptor.handleGetCategories();
    }

    // 推荐相关
    if (endpoint === '/recommend/popular' && method === 'get') {
      return MockAPIInterceptor.handleGetPopular();
    }
    if (endpoint === '/recommend/latest' && method === 'get') {
      return MockAPIInterceptor.handleGetLatest();
    }

    // 购物车相关
    if (endpoint === '/cart' && method === 'get') {
      return MockAPIInterceptor.handleGetCart();
    }
    if (endpoint === '/cart/add' && method === 'post') {
      return MockAPIInterceptor.handleAddToCart(data);
    }

    // 订单相关
    if (endpoint === '/orders' && method === 'post') {
      return MockAPIInterceptor.handleCreateOrder(data);
    }
    if (endpoint === '/orders' && method === 'get') {
      return MockAPIInterceptor.handleGetOrders();
    }

    // 地址相关
    if (endpoint === '/addresses' && method === 'get') {
      return MockAPIInterceptor.handleGetAddresses();
    }

    // 默认 404
    throw {
      statusCode: 404,
      type: ERROR_TYPES.SERVER_ERROR,
      message: `Mock API 暂未实现: ${method.toUpperCase()} ${endpoint}`,
      data: null,
    };
  }

  // ============ 用户相关处理 ============
  static handleRegister(data) {
    if (!data.email || !data.password || !data.username) {
      throw {
        statusCode: 400,
        type: ERROR_TYPES.VALIDATION_ERROR,
        message: '缺少必要参数',
        data: { field: 'email or password or username' },
      };
    }

    if (!data.email.endsWith('@seu.edu.cn')) {
      throw {
        statusCode: 400,
        type: ERROR_TYPES.VALIDATION_ERROR,
        message: '邮箱必须为SEU邮箱',
        data: { field: 'email' },
      };
    }

    if (data.email in mockUsers) {
      throw {
        statusCode: 400,
        type: ERROR_TYPES.VALIDATION_ERROR,
        message: '邮箱已被注册',
        data: { field: 'email' },
      };
    }

    const newUser = {
      id: Object.keys(mockUsers).length + 1,
      username: data.username,
      email: data.email,
      name: data.username,
      avatar: 'https://via.placeholder.com/100',
      phone: '',
      joinDate: new Date().toISOString().split('T')[0],
    };

    mockUsers[data.email] = newUser;

    return {
      statusCode: 200,
      data: {
        user: newUser,
        token: `mock-token-${Date.now()}`,
      },
    };
  }

  static handleLogin(data) {
    const { email, password } = data;

    if (!email || !password) {
      throw {
        statusCode: 400,
        type: ERROR_TYPES.VALIDATION_ERROR,
        message: '邮箱和密码不能为空',
        data: null,
      };
    }

    if (!(email in mockUsers)) {
      throw {
        statusCode: 401,
        type: ERROR_TYPES.AUTH_ERROR,
        message: '邮箱或密码错误',
        data: null,
      };
    }

    const user = mockUsers[email];

    return {
      statusCode: 200,
      data: {
        user,
        token: `mock-token-${Date.now()}`,
      },
    };
  }

  static handleGetCurrentUser() {
    // 如果有模拟的当前用户，返回它
    const currentUser = JSON.parse(localStorage.getItem('mockCurrentUser'));
    if (currentUser) {
      return {
        statusCode: 200,
        data: { user: currentUser },
      };
    }

    throw {
      statusCode: 401,
      type: ERROR_TYPES.AUTH_ERROR,
      message: '未登录',
      data: null,
    };
  }

  static handleGetUser(endpoint) {
    const userId = endpoint.split('/').pop();
    const user = Object.values(mockUsers).find(u => u.id == userId);

    if (!user) {
      throw {
        statusCode: 404,
        type: ERROR_TYPES.SERVER_ERROR,
        message: '用户不存在',
        data: null,
      };
    }

    return {
      statusCode: 200,
      data: { user },
    };
  }

  // ============ 商品相关处理 ============
  static handleSearchItems(params) {
    let results = [...mockItems];

    // 按关键词筛选
    if (params.q) {
      const q = params.q.toLowerCase();
      results = results.filter(
        item => item.title.toLowerCase().includes(q) ||
                 item.description.toLowerCase().includes(q)
      );
    }

    // 按分类筛选
    if (params.category) {
      results = results.filter(item => item.category === params.category);
    }

    // 按价格范围筛选
    if (params.minPrice) {
      results = results.filter(item => item.price >= params.minPrice);
    }
    if (params.maxPrice) {
      results = results.filter(item => item.price <= params.maxPrice);
    }

    // 排序
    if (params.sort) {
      if (params.sort === 'price_asc') {
        results.sort((a, b) => a.price - b.price);
      } else if (params.sort === 'price_desc') {
        results.sort((a, b) => b.price - a.price);
      } else if (params.sort === 'newest') {
        results.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      }
    }

    // 分页
    const page = params.page || 1;
    const pageSize = params.pageSize || 12;
    const start = (page - 1) * pageSize;
    const paginatedResults = results.slice(start, start + pageSize);

    return {
      statusCode: 200,
      data: {
        items: paginatedResults,
        total: results.length,
        page,
        pageSize,
        totalPages: Math.ceil(results.length / pageSize),
      },
    };
  }

  static handleGetItems(params) {
    return MockAPIInterceptor.handleSearchItems(params);
  }

  static handleGetItem(endpoint) {
    const itemId = endpoint.split('/').pop();
    const item = mockItems.find(i => i.id == itemId);

    if (!item) {
      throw {
        statusCode: 404,
        type: ERROR_TYPES.SERVER_ERROR,
        message: '商品不存在',
        data: null,
      };
    }

    return {
      statusCode: 200,
      data: { item },
    };
  }

  // ============ 分类相关处理 ============
  static handleGetCategories() {
    return {
      statusCode: 200,
      data: { categories: mockCategories },
    };
  }

  // ============ 推荐相关处理 ============
  static handleGetPopular() {
    return {
      statusCode: 200,
      data: {
        items: mockItems.sort((a, b) => b.reviews - a.reviews).slice(0, 4),
      },
    };
  }

  static handleGetLatest() {
    return {
      statusCode: 200,
      data: {
        items: mockItems
          .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
          .slice(0, 4),
      },
    };
  }

  static handleGetFeatured(params = {}) {
    const limit = Number(params.limit) || 4;
    return {
      statusCode: 200,
      data: {
        items: mockItems
          .sort((a, b) => b.reviews - a.reviews)
          .slice(0, limit),
      },
    };
  }

  // ============ 购物车相关处理 ============
  static handleGetCart() {
    return {
      statusCode: 200,
      data: {
        items: JSON.parse(sessionStorage.getItem('mockCart') || '[]'),
      },
    };
  }

  static handleAddToCart(data) {
    const cart = JSON.parse(sessionStorage.getItem('mockCart') || '[]');
    const existingItem = cart.find(item => item.id === data.itemId);

    if (existingItem) {
      existingItem.quantity += data.quantity || 1;
    } else {
      const item = mockItems.find(i => i.id === data.itemId);
      if (!item) {
        throw {
          statusCode: 404,
          type: ERROR_TYPES.SERVER_ERROR,
          message: '商品不存在',
          data: null,
        };
      }
      cart.push({
        id: item.id,
        title: item.title,
        price: item.price,
        image: item.images[0],
        quantity: data.quantity || 1,
      });
    }

    sessionStorage.setItem('mockCart', JSON.stringify(cart));

    return {
      statusCode: 200,
      data: { cart },
    };
  }

  // ============ 订单相关处理 ============
  static handleCreateOrder(data) {
    const cart = JSON.parse(sessionStorage.getItem('mockCart') || '[]');

    if (cart.length === 0) {
      throw {
        statusCode: 400,
        type: ERROR_TYPES.VALIDATION_ERROR,
        message: '购物车为空',
        data: null,
      };
    }

    const order = {
      id: `ORD-${Date.now()}`,
      items: cart,
      totalPrice: cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
      status: 'pending',
      createdAt: new Date().toISOString(),
      address: data.addressId,
      paymentMethod: data.paymentMethod,
    };

    sessionStorage.removeItem('mockCart');

    return {
      statusCode: 200,
      data: { order },
    };
  }

  static handleGetOrders() {
    return {
      statusCode: 200,
      data: {
        orders: [
          {
            id: 'ORD-1234567890',
            items: [mockItems[0]],
            totalPrice: mockItems[0].price,
            status: 'completed',
            createdAt: '2024-12-20',
          },
          {
            id: 'ORD-1234567891',
            items: [mockItems[1], mockItems[2]],
            totalPrice: mockItems[1].price + mockItems[2].price,
            status: 'shipped',
            createdAt: '2024-12-19',
          },
        ],
      },
    };
  }

  // ============ 地址相关处理 ============
  static handleGetAddresses() {
    return {
      statusCode: 200,
      data: {
        addresses: [
          {
            id: 1,
            name: '校内宿舍',
            detail: '九龙湖校区宿舍区A1栋302',
            isDefault: true,
          },
          {
            id: 2,
            name: '图书馆',
            detail: '丁家桥校区图书馆',
            isDefault: false,
          },
        ],
      },
    };
  }
}

/**
 * 启用 Mock API
 * 将原始的 fetch 包装起来，拦截 API 请求
 */
function enableMockAPI() {
  const originalFetch = window.fetch;

  window.fetch = async function(url, options = {}) {
    const urlObj = new URL(url, window.location.origin);
    const pathname = urlObj.pathname;

    // 只拦截 /api 开头的请求
    if (!pathname.startsWith('/api')) {
      return originalFetch.apply(this, arguments);
    }

    try {
      const method = (options.method || 'GET').toLowerCase();
      let data = null;

      // 解析请求数据
      if (method === 'post' || method === 'put') {
        if (options.body) {
          data = JSON.parse(options.body);
        }
      } else {
        // GET 请求从 URL 查询参数中提取
        data = Object.fromEntries(urlObj.searchParams);
      }

      // 移除 /api 前缀获取端点
      const endpoint = pathname.replace('/api', '');

      // 调用 Mock 拦截器
      const response = await MockAPIInterceptor.intercept(endpoint, method, data);

      // 返回 Mock 响应
      return new Response(JSON.stringify(response), {
        status: response.statusCode,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      console.error('[Mock API Error]', error);

      const response = {
        statusCode: error.statusCode || 500,
        type: error.type || ERROR_TYPES.UNKNOWN_ERROR,
        message: error.message || '未知错误',
        data: error.data || null,
      };

      return new Response(JSON.stringify(response), {
        status: response.statusCode,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }
  };

  console.log('✅ Mock API 已启用 - 所有 API 请求将使用模拟数据');
}

// 允许通过 localStorage 持久化开关，便于刷新后仍保持 Mock 状态
const mockFlag = window.USE_MOCK_API === true || localStorage.getItem('USE_MOCK_API') === 'true';
if (mockFlag) {
  window.USE_MOCK_API = true;
  enableMockAPI();
}

// 控制台可调用：setMockAPIEnabled(true/false)，同时刷新页面
window.setMockAPIEnabled = (enabled) => {
  localStorage.setItem('USE_MOCK_API', enabled ? 'true' : 'false');
  window.USE_MOCK_API = enabled === true;
  if (enabled) {
    enableMockAPI();
  }
  location.reload();
};
