/**
 * ============================================
 * SEU 校园二手交易平台 - 主JS文件
 * 提供通用功能和事件处理
 * ============================================
 */

/**
 * 应用全局状态
 */
const AppState = {
  currentUser: null,
  cart: [],
  isLoading: false,
};

/**
 * 通知/提示管理器
 */
const NotificationManager = {
  /**
   * 显示成功提示
   */
  success: (message, duration = 3000) => {
    NotificationManager.show(message, 'success', duration);
  },

  /**
   * 显示错误提示
   */
  error: (message, duration = 3000) => {
    NotificationManager.show(message, 'error', duration);
  },

  /**
   * 显示警告提示
   */
  warning: (message, duration = 3000) => {
    NotificationManager.show(message, 'warning', duration);
  },

  /**
   * 显示信息提示
   */
  info: (message, duration = 3000) => {
    NotificationManager.show(message, 'info', duration);
  },

  /**
   * 通用显示函数
   */
  show: (message, type = 'info', duration = 3000) => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert--${type}`;
    alertDiv.innerHTML = `
      <div>${message}</div>
      <span class="alert__close">&times;</span>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 关闭按钮事件
    alertDiv.querySelector('.alert__close').addEventListener('click', () => {
      alertDiv.remove();
    });
    
    // 自动关闭
    if (duration > 0) {
      setTimeout(() => {
        alertDiv.remove();
      }, duration);
    }
  },
};

/**
 * 表单验证管理器
 */
const FormValidator = {
  /**
   * 验证电子邮件
   */
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  /**
   * 验证 SEU 邮箱
   */
  isValidSEUEmail: (email) => {
    return /^[^\s@]+@seu\.edu\.cn$/.test(email);
  },

  /**
   * 验证密码强度
   */
  validatePassword: (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push('密码至少需要8个字符');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('密码需要包含小写字母');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('密码需要包含大写字母');
    }
    if (!/[0-9]/.test(password)) {
      errors.push('密码需要包含数字');
    }
    return {
      isValid: errors.length === 0,
      errors,
    };
  },

  /**
   * 验证用户名
   */
  isValidUsername: (username) => {
    return /^[a-zA-Z0-9_]{3,16}$/.test(username);
  },

  /**
   * 验证表单字段
   */
  validateField: (name, value) => {
    const validators = {
      email: (val) => {
        if (!val) return '邮箱不能为空';
        if (!FormValidator.isValidEmail(val)) return '邮箱格式不正确';
        return null;
      },
      seu_email: (val) => {
        if (!val) return '邮箱不能为空';
        if (!FormValidator.isValidSEUEmail(val)) return '请使用 SEU 邮箱 (@seu.edu.cn)';
        return null;
      },
      password: (val) => {
        if (!val) return '密码不能为空';
        const validation = FormValidator.validatePassword(val);
        return validation.isValid ? null : validation.errors[0];
      },
      username: (val) => {
        if (!val) return '用户名不能为空';
        if (!FormValidator.isValidUsername(val)) {
          return '用户名必须为3-16个字符，只能包含字母、数字和下划线';
        }
        return null;
      },
      required: (val) => {
        return val ? null : '此字段不能为空';
      },
    };

    const validator = validators[name];
    return validator ? validator(value) : null;
  },
};

/**
 * 购物车管理器
 */
const CartManager = {
  /**
   * 获取购物车数据
   */
  getCart: () => AppState.cart,

  /**
   * 从本地存储加载购物车
   */
  loadCart: () => {
    const stored = sessionStorage.getItem('cart');
    AppState.cart = stored ? JSON.parse(stored) : [];
    CartManager.updateCartUI();
  },

  /**
   * 保存购物车到本地存储
   */
  saveCart: () => {
    sessionStorage.setItem('cart', JSON.stringify(AppState.cart));
    CartManager.updateCartUI();
  },

  /**
   * 添加商品到购物车
   */
  addItem: (item) => {
    const existing = AppState.cart.find(i => i.itemId === item.itemId);
    if (existing) {
      existing.quantity += item.quantity || 1;
    } else {
      AppState.cart.push({
        ...item,
        quantity: item.quantity || 1,
      });
    }
    CartManager.saveCart();
    NotificationManager.success(`"${item.title}" 已添加到购物车`);
  },

  /**
   * 移除购物车商品
   */
  removeItem: (itemId) => {
    AppState.cart = AppState.cart.filter(i => i.itemId !== itemId);
    CartManager.saveCart();
    NotificationManager.success('已从购物车移除');
  },

  /**
   * 更新商品数量
   */
  updateQuantity: (itemId, quantity) => {
    const item = AppState.cart.find(i => i.itemId === itemId);
    if (item) {
      if (quantity <= 0) {
        CartManager.removeItem(itemId);
      } else {
        item.quantity = quantity;
        CartManager.saveCart();
      }
    }
  },

  /**
   * 清空购物车
   */
  clear: () => {
    AppState.cart = [];
    CartManager.saveCart();
  },

  /**
   * 获取购物车统计
   */
  getStats: () => {
    const total = AppState.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    return {
      count: AppState.cart.reduce((sum, item) => sum + item.quantity, 0),
      total: total.toFixed(2),
      items: AppState.cart.length,
    };
  },

  /**
   * 更新购物车UI
   */
  updateCartUI: () => {
    const stats = CartManager.getStats();
    
    // 更新购物车徽章
    const badge = document.querySelector('.navbar__badge');
    if (badge && stats.count > 0) {
      badge.textContent = stats.count;
      badge.style.display = 'flex';
    } else if (badge) {
      badge.style.display = 'none';
    }

    // 触发自定义事件
    window.dispatchEvent(new CustomEvent('cartUpdated', { detail: stats }));
  },
};

/**
 * 用户认证管理器
 */
const AuthManager = {
  /**
   * 保存用户信息
   */
  setUser: (user) => {
    AppState.currentUser = user;
    localStorage.setItem('user', JSON.stringify(user));
  },

  /**
   * 获取用户信息
   */
  getUser: () => {
    if (!AppState.currentUser) {
      const stored = localStorage.getItem('user');
      AppState.currentUser = stored ? JSON.parse(stored) : null;
    }
    return AppState.currentUser;
  },

  /**
   * 检查是否已登录
   */
  isLoggedIn: () => {
    return AuthManager.getUser() !== null;
  },

  /**
   * 登出
   */
  logout: () => {
    AppState.currentUser = null;
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  },

  /**
   * 更新UI
   */
  updateUI: () => {
    const user = AuthManager.getUser();
    const userMenuEl = document.querySelector('.navbar__user-menu');
    
    if (!userMenuEl) return;

    if (user) {
      userMenuEl.innerHTML = `
        <span>欢迎，${user.username}</span>
        <a href="/publish-item" class="btn btn--primary btn--sm">发布商品</a>
        <a href="/cart" class="navbar__link">
          购物车
          <span class="navbar__badge" style="display: none;">0</span>
        </a>
        <a href="/profile" class="navbar__link">个人资料</a>
        <button class="btn btn--text" id="logout-btn">登出</button>
      `;
      
      // 登出事件
      document.getElementById('logout-btn').addEventListener('click', async () => {
        try {
          await API.user.logout();
          AuthManager.logout();
          NotificationManager.success('已登出');
          setTimeout(() => {
            window.location.href = '/';
          }, 1000);
        } catch (error) {
          NotificationManager.error('登出失败');
        }
      });
    } else {
      userMenuEl.innerHTML = `
        <a href="/login?redirect=/publish-item" class="btn btn--primary btn--sm">发布商品</a>
        <a href="/login" class="navbar__link">登录</a>
        <a href="/register" class="btn btn--primary">注册</a>
      `;
    }
  },
};

/**
 * DOM 工具函数
 */
const DOMUtils = {
  /**
   * 安全获取元素
   */
  query: (selector) => document.querySelector(selector),

  /**
   * 获取所有匹配元素
   */
  queryAll: (selector) => document.querySelectorAll(selector),

  /**
   * 检查元素是否有某个类
   */
  hasClass: (el, className) => el.classList.contains(className),

  /**
   * 添加类
   */
  addClass: (el, className) => el.classList.add(className),

  /**
   * 移除类
   */
  removeClass: (el, className) => el.classList.remove(className),

  /**
   * 切换类
   */
  toggleClass: (el, className) => el.classList.toggle(className),

  /**
   * 显示元素
   */
  show: (el) => {
    if (el) el.style.display = '';
  },

  /**
   * 隐藏元素
   */
  hide: (el) => {
    if (el) el.style.display = 'none';
  },

  /**
   * 获取表单数据
   */
  getFormData: (form) => {
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
      data[key] = value;
    });
    return data;
  },
};

/**
 * 加载管理器
 */
const LoadingManager = {
  /**
   * 显示加载状态
   */
  show: (message = '加载中...') => {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'modal is-open';
    loadingDiv.id = 'loading-modal';
    loadingDiv.innerHTML = `
      <div class="modal__content flex flex--center flex--col gap-lg">
        <div class="loading"></div>
        <p>${message}</p>
      </div>
    `;
    document.body.appendChild(loadingDiv);
    AppState.isLoading = true;
  },

  /**
   * 隐藏加载状态
   */
  hide: () => {
    const loadingDiv = document.getElementById('loading-modal');
    if (loadingDiv) {
      loadingDiv.remove();
    }
    AppState.isLoading = false;
  },
};

/**
 * 页面初始化
 */
function initPage() {
  // 加载购物车
  CartManager.loadCart();

  // 初始化用户认证 UI
  AuthManager.updateUI();

  // 设置 API 错误处理
  if (typeof setupAPIErrorHandling === 'function') {
    setupAPIErrorHandling();
  }

  // 添加全局导航事件
  setupNavigation();
}

/**
 * 设置导航事件
 */
function setupNavigation() {
  // 搜索功能
  const searchForm = document.querySelector('.navbar__search');
  if (searchForm) {
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = searchForm.querySelector('input');
      if (input && input.value.trim()) {
        window.location.href = `/search?query=${encodeURIComponent(input.value)}`;
      }
    });
  }

  // 购物车链接
  const cartLink = document.querySelector('.navbar__cart');
  if (cartLink) {
    cartLink.addEventListener('click', () => {
      window.location.href = '/cart';
    });
  }
}

/**
 * DOM 加载完成后初始化
 */
document.addEventListener('DOMContentLoaded', initPage);

/**
 * 导出工具函数供其他脚本使用
 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AppState,
    NotificationManager,
    FormValidator,
    CartManager,
    AuthManager,
    DOMUtils,
    LoadingManager,
  };
}