# 路由定义文件
from flask import render_template, jsonify, request

def register_routes(app):
    """
    注册所有应用路由
    """
    
    # ============ 页面路由 ============
    
    @app.route('/')
    def index():
        """首页"""
        return render_template('index.html')
    
    @app.route('/register')
    def register():
        """注册页"""
        return render_template('register.html')
    
    @app.route('/login')
    def login():
        """登录页"""
        return render_template('login.html')
    
    @app.route('/items')
    def items():
        """搜索/浏览页"""
        return render_template('items.html')
    
    @app.route('/search')
    def search():
        """搜索结果页"""
        query = request.args.get('query', '')
        return render_template('items.html', search_query=query)
    
    @app.route('/items/<int:item_id>')
    def item_detail(item_id):
        """商品详情页"""
        return render_template('item_detail.html', item_id=item_id)
    
    @app.route('/cart')
    def cart():
        """购物车页"""
        return render_template('cart.html')
    
    @app.route('/checkout')
    def checkout():
        """结账页"""
        return render_template('checkout.html')
    
    @app.route('/profile')
    def profile():
        """个人资料页"""
        return render_template('profile.html')
    
    # ============ 信息页面 ============
    
    @app.route('/about')
    def about():
        """平台介绍页"""
        return render_template('about.html')
    
    @app.route('/guide')
    def guide():
        """使用指南页"""
        return render_template('guide.html')
    
    @app.route('/contact')
    def contact():
        """联系我们页"""
        return render_template('contact.html')
    
    @app.route('/publish')
    def publish():
        """如何发布商品页"""
        return render_template('publish.html')
    
    @app.route('/buying-guide')
    def buying_guide():
        """购买指南页"""
        return render_template('buying-guide.html')
    
    @app.route('/delivery')
    def delivery():
        """配送说明页"""
        return render_template('delivery.html')
    
    @app.route('/delivery-points')
    def delivery_points():
        """配送地点页"""
        return render_template('delivery-points.html')
    
    @app.route('/faq')
    def faq():
        """常见问题页"""
        return render_template('faq.html')
    
    @app.route('/terms')
    def terms():
        """使用条款页"""
        return render_template('terms.html')
    
    # ============ API 路由（Mock 数据用） ============
    
    
    @app.route('/api/cart', methods=['GET'])
    def api_get_cart():
        """获取购物车 API"""
        return jsonify({
            'statusCode': 200,
            'data': {'items': []}
        })
    
    @app.route('/api/cart/add', methods=['POST'])
    def api_add_to_cart():
        """添加到购物车 API"""
        return jsonify({
            'statusCode': 200,
            'data': {'cart': []}
        })
    
    @app.route('/api/orders', methods=['POST'])
    def api_create_order():
        """创建订单 API"""
        return jsonify({
            'statusCode': 200,
            'data': {'order': None}
        })
    
    @app.route('/api/orders', methods=['GET'])
    def api_get_orders():
        """获取订单列表 API"""
        return jsonify({
            'statusCode': 200,
            'data': {'orders': []}
        })
    
    @app.route('/api/addresses', methods=['GET'])
    def api_get_addresses():
        """获取地址列表 API"""
        return jsonify({
            'statusCode': 200,
            'data': {'addresses': []}
        })
    
    # ============ 错误处理 ============
    
    @app.errorhandler(404)
    def not_found(error):
        """404 错误处理"""
        return jsonify({
            'statusCode': 404,
            'type': 'SERVER_ERROR',
            'message': '页面不存在'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 错误处理"""
        return jsonify({
            'statusCode': 500,
            'type': 'SERVER_ERROR',
            'message': '服务器错误'
        }), 500