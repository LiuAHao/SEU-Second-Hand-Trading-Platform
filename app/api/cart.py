"""
购物车API接口
处理基于Session的购物车操作
注意：购物车数据存储在Session中，不存储在数据库
"""
from flask import Blueprint, request, session
from app.utils.response import APIResponse

cart_bp = Blueprint('cart_api', __name__, url_prefix='/cart')

# -------------------------- 1. 获取购物车 --------------------------
@cart_bp.route('/', methods=['GET'])
def get_cart():
    """获取购物车内容"""
    cart = session.get('cart', [])
    return APIResponse.success(
        message='获取成功',
        data={'items': cart, 'total': len(cart)}
    )

# -------------------------- 2. 添加商品到购物车 --------------------------
@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """添加商品到购物车"""
    data = request.json or {}
    item_id = data.get('itemId')
    title = data.get('title', '')
    price = data.get('price', 0)
    quantity = data.get('quantity', 1)
    image = data.get('image', '')

    if not item_id:
        return APIResponse.validation_error(errors={'itemId': '商品ID不能为空'})

    if quantity <= 0:
        return APIResponse.validation_error(errors={'quantity': '数量必须大于0'})

    # 获取当前购物车
    cart = session.get('cart', [])

    # 检查商品是否已在购物车中
    for item in cart:
        if item['itemId'] == item_id:
            item['quantity'] += quantity
            session['cart'] = cart
            return APIResponse.success(
                message='已更新购物车数量',
                data={'cart': cart}
            )

    # 添加新商品到购物车
    cart.append({
        'itemId': item_id,
        'title': title,
        'price': price,
        'quantity': quantity,
        'image': image
    })

    session['cart'] = cart
    return APIResponse.success(
        message='已添加到购物车',
        data={'cart': cart}
    )

# -------------------------- 3. 更新购物车商品数量 --------------------------
@cart_bp.route('/update/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    """更新购物车中商品的数量"""
    data = request.json or {}
    quantity = data.get('quantity', 1)

    if quantity <= 0:
        return APIResponse.validation_error(errors={'quantity': '数量必须大于0'})

    cart = session.get('cart', [])

    for item in cart:
        if item['itemId'] == item_id:
            item['quantity'] = quantity
            session['cart'] = cart
            return APIResponse.success(
                message='已更新数量',
                data={'cart': cart}
            )

    return APIResponse.not_found(message='商品不在购物车中')

# -------------------------- 4. 从购物车移除商品 --------------------------
@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    """从购物车中移除商品"""
    cart = session.get('cart', [])

    # 过滤掉要删除的商品
    new_cart = [item for item in cart if item['itemId'] != item_id]

    if len(new_cart) == len(cart):
        return APIResponse.not_found(message='商品不在购物车中')

    session['cart'] = new_cart
    return APIResponse.success(
        message='已从购物车移除',
        data={'cart': new_cart}
    )

# -------------------------- 5. 清空购物车 --------------------------
@cart_bp.route('/clear', methods=['POST'])
def clear_cart():
    """清空购物车"""
    session['cart'] = []
    return APIResponse.success(
        message='购物车已清空',
        data={'cart': []}
    )

# -------------------------- 6. 获取购物车统计信息 --------------------------
@cart_bp.route('/stats', methods=['GET'])
def get_cart_stats():
    """获取购物车统计信息"""
    cart = session.get('cart', [])

    total_items = sum(item['quantity'] for item in cart)
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    total_kinds = len(cart)

    return APIResponse.success(
        message='获取成功',
        data={
            'count': total_items,
            'items': total_kinds,
            'total': round(total_price, 2)
        }
    )
