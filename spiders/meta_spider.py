from concurrent.futures import ThreadPoolExecutor
import datetime
import json
import random
import os
import sys
import time
import traceback

CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(CURRENT_PATH, "../"))

from config import GROUP_INFO_URL, INNER_GROUP_INFO_URL
from util import get_redis_cli
from util import meta_logger
from util import proxy_request_get


def spide_group_meta():
    """
    获取全部图片组 meta 信息，并将其存入数据库
    """
    meta_logger.info("下载图片组信息")
    redis_cli = get_redis_cli()

    origin_meta_str = redis_cli.get("group:meta")
    origin_meta_str = b"[]" if origin_meta_str is None else origin_meta_str
    origin_meta = json.loads(origin_meta_str.decode("utf8"))  # 原 meta 数据
    meta_logger.info("原组长: {}".format(len(origin_meta)))
    origin_group_index_set = {meta["id"] for meta in origin_meta}  # 原来所有图片组的 id 集合

    try:
        remote_meta = json.loads(
            proxy_request_get(GROUP_INFO_URL).content.decode("utf8")
        )["indexes"]
    except:
        meta_logger.error('退出: 下载"全部"图片组信息失败')
        meta_logger.error(traceback.format_exc())
    else:  # 爬取成功
        counter = 0
        for meta in remote_meta:
            if meta["index"] not in origin_group_index_set:  # 不在原来的数据里，添加
                new_meta_unit = {
                    "id": meta["index"],
                    "group_name": meta["des"],
                    "origin_url": meta["url"],
                    "nos_key": "",
                    "nos_url": "",
                    "local_file_path": ""
                }
                origin_meta = [new_meta_unit] + origin_meta
                counter += 1
        redis_cli.set("group:meta", json.dumps(origin_meta).encode("utf8"))
        meta_logger.info("退出: 新增图片组信息 {} 组".format(counter))
    return origin_meta


def single_spide_group(group_id):
    time.sleep(random.random() / 10)
    meta_logger.info("{}: 图片组信息下载".format(group_id))
    inner_group_info_url = INNER_GROUP_INFO_URL.format(index=group_id)

    redis_cli = get_redis_cli()
    group_key = "group:{}".format(group_id)

    origin_group_info_str = redis_cli.get(group_key)
    origin_group_info_str = b"[]" if origin_group_info_str is None else origin_group_info_str
    origin_group_info = json.loads(origin_group_info_str.decode("utf8"))  # 原 meta 数据
    meta_logger.info("{}: 原图片数量: {}".format(group_id, len(origin_group_info)))
    origin_img_index_set = {img_info["id"] for img_info in origin_group_info}  # 原来组内所有图片的 id

    try:
        remote_group_info = json.loads(
            proxy_request_get(inner_group_info_url).content.decode("utf8")
        )["info"]
    except:
        meta_logger.error("{}: 退出: 下载图片组信息失败".format(group_id))
        meta_logger.error(traceback.format_exc())
        return False
    else:  # 爬取成功
        counter = 0
        for group_info in remote_group_info:
            if group_info["id"] not in origin_img_index_set:  # 不在原来的数据里，添加
                new_image_info = {
                    "id": group_info["id"],
                    "group_id": group_id,
                    "origin_url": group_info["url"],
                    "nos_key": "",
                    "nos_url": "",
                    "local_file_path": "",
                    "file_name": str(group_info["url"]).split("/")[-1]
                }
                origin_group_info = [new_image_info] + origin_group_info
                counter += 1
        redis_cli.set(group_key, json.dumps(origin_group_info).encode("utf8"))
        meta_logger.info("{}: 退出: 新增图片 {} 张".format(group_id, counter))
    return True


def spide_group(group_meta):
    """
    多线程 (16) 爬取图片组信息，并将其存入数据库
    :return:
    """
    meta_logger.info("多线程爬取图片组信息，任务共: {}".format(len(group_meta)))
    success_counter = 0
    fail_counter = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        for status in executor.map(single_spide_group, iter(meta["id"] for meta in group_meta)):
            if status:
                success_counter += 1
            else:
                fail_counter += 1
    meta_logger.info("多线程爬取图片组信息，成功-{}，失败-{}".format(success_counter, fail_counter))


def main():
    group_meta = spide_group_meta()
    spide_group(group_meta)


if __name__ == "__main__":
    main()
    while True:
        if datetime.datetime.now().hour == 3:
            if datetime.datetime.now().minute <= 5:
                main()
        time.sleep(5 * 60 - 5)

