# -*- coding: utf-8 -*-
# 安全工具模块
import time
import hashlib
from functools import wraps
from flask import request, g, current_app
import redis
from app.schemas.response import BaseResponse

# Redis连接将在应用程序初始化时设置
redis_client = None

def init_redis(app):
    """初始化Redis连接"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=app.config.get('REDIS_HOST', 'localhost'),
            port=app.config.get('REDIS_PORT', 6379),
            db=app.config.get('REDIS_DB', 1),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # 测试连接
        redis_client.ping()
        print("Redis连接成功")
    except Exception as e:
        print(f"Redis连接失败: {e}")
        redis_client = None

def get_client_identifier(by="ip"):
    """
    获取客户端标识符
    
    :param by: 标识符类型："ip"表示按IP地址，"user"表示按用户ID
    :return: 客户端标识符字符串
    """
    if by == "ip":
        # 获取客户端IP
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            return request.environ['REMOTE_ADDR']
        else:
            return request.environ['HTTP_X_FORWARDED_FOR']
    elif by == "user":
        # 按用户ID限制，需要用户已认证
        if hasattr(g, 'user_id') and g.user_id:
            return str(g.user_id)
        else:
            # 如果用户未认证，回退到IP限制
            return get_client_identifier("ip")
    else:
        # 默认按IP限制
        return get_client_identifier("ip")

def rate_limit(max_requests=60, window=60, by="ip", redis_prefix="rate_limit"):
    """
    限流频率装饰器，使用Redis实现
    
    :param max_requests: 时间窗口内的最大请求数
    :param window: 时间窗口，秒
    :param by: 限制类型："ip"表示按IP地址限制，"user"表示按用户ID限制
    :param redis_prefix: Redis键前缀
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 如果Redis不可用，跳过频率限制
            if redis_client is None:
                print("Redis不可用，跳过频率限制")
                return f(*args, **kwargs)
            
            # 获取客户端标识符
            identifier = get_client_identifier(by)
            
            # 构造键名
            key = f"{redis_prefix}:{identifier}:{request.endpoint}"
            
            # 获取当前时间
            now = time.time()
            pipeline = redis_client.pipeline()
            
            # 使用Redis滑动窗口记录请求记录
            pipeline.zremrangebyscore(key, 0, now - window)
            pipeline.zadd(key, {str(now): now})
            pipeline.expire(key, int(window))
            pipeline.zcard(key)
            
            try:
                results = pipeline.execute()
                current_requests = results[3]  # zcard的结果
                
                if current_requests >= max_requests:
                    print(f"频率限制触发: {identifier} 已达到 {current_requests}/{max_requests} 请求")
                    return BaseResponse.error(429, "请求过于频繁，请稍后重试").dict(), 429
                
                return f(*args, **kwargs)
            except redis.RedisError as e:
                # Redis错误时，记录日志但不阻止请求
                print(f"Redis错误，跳过频率限制: {e}")
                return f(*args, **kwargs)
            except Exception as e:
                print(f"频率限制异常: {e}")
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def validate_json(f):
    """
    验证JSON数据装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return BaseResponse.error(400, "请求必须是JSON格式").dict()
        
        try:
            data = request.get_json()
            if data is None:
                return BaseResponse.error(400, "无效的JSON数据").dict()
        except Exception as e:
            print(f"JSON解析错误: {str(e)}")
            return BaseResponse.error(400, "无效的JSON数据").dict()
        
        # 清理输入数据
        cleaned_data = sanitize_input(data)
        # 正确设置缓存：Flask 的 _cached_json 是一个字典，键是 silent 参数
        request._cached_json = {False: cleaned_data, True: cleaned_data}
        
        return f(*args, **kwargs)
    
    return decorated_function

def sanitize_input(data):
    """
    清理输入数据，防止XSS等攻击
    """
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # 简单的HTML标签转义
        return data.replace('<', '&lt;').replace('>', '&gt;')
    else:
        return data