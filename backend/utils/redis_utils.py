import redis
import utils.config_handler

def create_redis_client():
    REDIS_CONFIG = utils.config_handler.load_json_config()['redis_server']
    redis_client = redis.Redis(host=REDIS_CONFIG['host'], port=int(REDIS_CONFIG['port']))
    return redis_client