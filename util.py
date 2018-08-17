import logging
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler

import redis
import requests

from config import META_LOG_PATH, IMAGE_LOG_PATH
from config import GET_URI, DEL_URI
from config import REDIS_HOST, REDIS_PORT


# ----- LOGGERS ----- #
formatter = logging.Formatter(
    '%(asctime)s level-%(levelname)-8s: %(message)s'
)
std_handler = StreamHandler()
std_handler.setFormatter(formatter)

meta_logger = logging.getLogger("meta_logger")
meta_timed_rotating_file_handler = TimedRotatingFileHandler(META_LOG_PATH, 'midnight')
meta_timed_rotating_file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
meta_logger.addHandler(std_handler)
meta_logger.addHandler(meta_timed_rotating_file_handler)
meta_logger.setLevel(logging.DEBUG)

img_logger = logging.getLogger("meta_logger")
img_timed_rotating_file_handler = TimedRotatingFileHandler(IMAGE_LOG_PATH, 'midnight')
img_timed_rotating_file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
img_logger.addHandler(std_handler)
img_logger.addHandler(img_timed_rotating_file_handler)
img_logger.setLevel(logging.DEBUG)


# ----- PROXY ----- #

def get_proxy_ip():
    res = requests.get(GET_URI).content.decode("utf8")
    return res


def remove_proxy_ip(proxy):
    res = requests.get(DEL_URI.format(proxy=proxy)).content.decode("utf8")
    return res == "success"


def _simple_proxy_request_get(*args, **kwargs):
    """
    using proxy ip for request
    :param args:
    :param kwargs:
    :return:
    """
    proxy = get_proxy_ip()
    kwargs["proxies"] = kwargs.get(
        "proxies", {"http": "http://{}".format(proxy)}
    )
    kwargs["timeout"] = kwargs.get("timeout", 12)
    return proxy, requests.get(*args, **kwargs)


def proxy_request_get(*args, **kwargs):
    """
    retry simple_proxy_request_get 4 times
    :param args:
    :param kwargs:
    :return:
    """
    for _ in range(3):
        try:
            proxy, res = _simple_proxy_request_get(*args, **kwargs)
            return res
        except:
            remove_proxy_ip(proxy=proxy)
    return _simple_proxy_request_get(*args, **kwargs)[1]


# ----- PROXY ----- #

redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)


def get_redis_cli():
    return redis.StrictRedis(connection_pool=redis_pool)
