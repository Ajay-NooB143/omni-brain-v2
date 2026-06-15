import os
import time
import redis


def get_redis_connection(host=None, port=None, password=None, max_retries=3):
    """Redis connection with retry + exponential backoff"""
    host = host or os.getenv('REDIS_HOST', 'localhost')
    port = port or int(os.getenv('REDIS_PORT', '6379'))
    password = password or os.getenv('REDIS_PASSWORD')

    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=host, port=port, password=password,
                decode_responses=True, socket_timeout=5
            )
            r.ping()
            return r
        except (redis.ConnectionError, redis.TimeoutError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise ConnectionError(f"Redis unavailable after {max_retries} attempts: {e}")


def validate_signal(signal_dict):
    """Validate required signal fields"""
    required = ['pair', 'direction', 'entry', 'size']
    for field in required:
        if field not in signal_dict or signal_dict[field] is None:
            raise ValueError(f"Missing required field: {field}")
    if signal_dict['direction'] not in ['BUY', 'SELL']:
        raise ValueError("Direction must be BUY or SELL")
    if signal_dict['size'] <= 0:
        raise ValueError("Size must be > 0")
    return True
