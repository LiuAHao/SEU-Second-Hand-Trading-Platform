"""
购物车业务逻辑服务
处理基于Session的购物车操作
注意：购物车数据存储在Session中，不存储在数据库！
"""


class CartService:
    """购物车服务类"""
    
    @staticmethod
    def get_cart(session):
        """
        获取购物车
        TODO: 从Session中读取购物车数据
        - 检查库存是否仍充足
        - 计算购物车统计（总件数、总金额）
        """
        pass
    
    @staticmethod
    def add_to_cart(session, item_id, quantity):
        """
        添加到购物车
        TODO: 将商品添加到Session中的购物车
        - 检查商品是否存在
        - 检查库存是否充足
        """
        pass
    
    @staticmethod
    def update_cart_item(session, item_id, quantity):
        """
        修改购物车项数量
        TODO: 更新Session中的购物车项
        """
        pass
    
    @staticmethod
    def remove_from_cart(session, item_id):
        """
        删除购物车项
        TODO: 从Session中删除特定商品
        """
        pass
    
    @staticmethod
    def clear_cart(session):
        """
        清空购物车
        TODO: 清空Session中的所有购物车数据
        """
        pass
    
    @staticmethod
    def get_cart_stats(session):
        """
        获取购物车统计
        - 总件数
        - 总金额
        - 商品数量
        """
        pass
