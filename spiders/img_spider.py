from concurrent.futures import ThreadPoolExecutor
import requests
import dbm
import os
import time
import random
import json

from config import META_KEY, KEY_TEMPLATE
from util import IMAGE_LOG_PATH
from util import get_redis_cli


# def get_and_save_image(url, file_path):
#     try:
#         res = requests.get(
#             url,
#             proxies={"http": "http://{}".format(proxy)}
#         )
#         p_file = open(file_path, 'wb')
#         p_file.write(res.content)
#         p_file.close()
#     except Exception as e:
#         print("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))
#         error_logger.info("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))
#         try:
#             proxy = get_proxy()
#             res = requests.get(
#                 url,
#                 proxies={"http": "http://{}".format(proxy)}
#             )
#             p_file = open(file_path, 'wb')
#             p_file.write(res.content)
#             p_file.close()
#         except Exception as e:
#             print("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))
#             error_logger.info("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))


def get_unfinished_images():
    """
    获取全部未完成下载图片的生成器
    :return:
    """
    redis_cli = get_redis_cli()
    all_groups = json.loads(redis_cli.get(META_KEY).decode("utf8"))
    for group in all_groups:
        group_id = group["id"]
        all_images = json.loads(
            redis_cli.get(KEY_TEMPLATE.format(idx=group_id)).decode("utf8")
        )
        yield from (img_info for img_info in all_images if not img_info["finish"])


def download_and_upload_image():

    pass


def main():
    unfinished_images = get_unfinished_images()
    for img_info in unfinished_images:
        origin_url = img_info["origin_url"]
        time.sleep(1)


if __name__ == "__main__":
    main()
