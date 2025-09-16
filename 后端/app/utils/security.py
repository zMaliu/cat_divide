import time
import hashlib
from functools import wraps
from flask import request, g, current_app
import redis
from app.schemas.response import BaseResponse

# Redis连接将在应用初始化时设置
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
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        redis_client = None

def get_client_identifier(by="ip"):
    """
    获取客户端标识符
    
    :param by: 标识符类型，"ip"表示按IP地址，"user"表示按用户ID
    :return: 客户端标识符字符串
    """
    if by == "ip":
        # 获取客户端IP
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            return request.environ['REMOTE_ADDR']
        else:
            return request.environ['HTTP_X_FORWARDED_FOR']
    elif by == "user":
        # 按用户ID限制（需要用户已认证）
        if hasattr(g, 'user_id') and g.user_id:
            return str(g.user_id)
        else:
            # 如果用户未认证，回退到按IP限制
            return get_client_identifier("ip")
    else:
        # 默认按IP限制
        return get_client_identifier("ip")

def rate_limit(max_requests=60, window=60, by="ip", redis_prefix="rate_limit"):
    """
    请求频率限制装饰器（基于Redis实现）
    
    :param max_requests: 时间窗口内的最大请求数
    :param window: 时间窗口（秒）
    :param by: 限制依据，"ip"表示按IP地址限制，"user"表示按用户ID限制
    :param redis_prefix: Redis键前缀
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 如果Redis不可用，跳过频率限制
            if redis_client is None:
                print("⚠️ Redis不可用，跳过频率限制")
                return f(*args, **kwargs)
            
            # 获取客户端标识符
            identifier = get_client_identifier(by)
            
            # 生成限流键
            key = f"{redis_prefix}:{identifier}:{request.endpoint}"
            
            # 获取当前时间戳
            now = time.time()
            pipeline = redis_client.pipeline()
            
            # 使用Redis事务清理过期记录并添加新记录
            pipeline.zremrangebyscore(key, 0, now - window)
            pipeline.zadd(key, {str(now): now})
            pipeline.expire(key, int(window))
            pipeline.zcard(key)
            
            try:
                results = pipeline.execute()
                request_count = results[3]  # zcard的结果
                
                if request_count > max_requests:
                    return BaseResponse.error(429, "请求过于频繁，请稍后再试").dict(), 429
                
                return f(*args, **kwargs)
            except redis.RedisError as e:
                # Redis出错时，记录日志但不阻止请求
                print(f"⚠️ Redis错误，跳过频率限制: {e}")
                return f(*args, **kwargs)
            except Exception as e:
                # 其他异常，记录日志但不阻止请求
                print(f"⚠️ 频率限制出现异常，跳过限制: {e}")
                return f(*args, **kwargs)
                
        return decorated_function
    return decorator

def validate_json(f):
    """
    验证JSON请求体的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return BaseResponse.error(400, "请求体必须是JSON格式").dict(), 400
            
            # 检查请求体大小
            content_length = request.content_length
            if content_length and content_length > 10 * 1024 * 1024:  # 10MB
                return BaseResponse.error(400, "请求体过大").dict(), 400
                
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(data):
    """
    简单的输入清理函数
    """
    if isinstance(data, str):
        # 移除潜在的危险字符
        # 注意：这只是基础的清理，实际应用中应根据具体需求进行处理
        data = data.replace('<', '&lt;').replace('>', '&gt;')
        return data.strip()
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data