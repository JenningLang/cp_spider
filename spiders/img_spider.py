from concurrent.futures import ThreadPoolExecutor
import os
import sys
import time
import json
import traceback
from threading import Lock

CURRENT_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(CURRENT_PATH, "../"))

from config import CURRENT_PATH, META_KEY, KEY_TEMPLATE
from oss import put_image
from util import img_logger
from util import get_redis_cli
from util import proxy_request_get


LOCK = Lock()


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
        yield from (img_info for img_info in all_images if img_info["nos_key"] == "")


def download_image(url):
    """
    下载到: ../data/tmp_img
    :param url:
    :return:
    """
    img_name = str(url).split("/")[-1]
    file_path = os.path.join(CURRENT_PATH, "./data/tmp_img/{}".format(img_name))
    res = proxy_request_get(url)
    with open(file_path, 'wb') as p_file:
        p_file.write(res.content)

    return file_path


def upload_image(img_path, group_id):
    """
    将文件上传到 oss
    :param img_path:
    :param group_id:
    :return:
    """
    return put_image(img_path=img_path, group_name=group_id)[0]


def revise_meta(group_id, img_id, key):
    """
    填充 nos_key, nos_url
    :param group_id:
    :param img_id:
    :return:
    """
    LOCK.acquire()
    redis_cli = get_redis_cli()
    img_info_list = json.loads(redis_cli.get(KEY_TEMPLATE.format(idx=group_id)).decode("utf8"))
    for info in img_info_list:
        if info["id"] == img_id:
            info["nos_key"] = key
            break
    redis_cli.set(
        KEY_TEMPLATE.format(idx=group_id), json.dumps(img_info_list)
    )
    LOCK.release()


def del_image(file_path):
    """
    删除本地的图片缓存
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def process_image(img_info):
    """
    下载、上传、修改原来组的状态(加锁)、删除
    :param img_info:
    :return:
    """
    time.sleep(0.25)
    try:
        file_path = download_image(url=img_info["origin_url"])
        oss_key = upload_image(img_path=file_path, group_id=img_info["group_id"])
        revise_meta(group_id=img_info["group_id"], img_id=img_info["id"], key=oss_key)
        del_image(file_path=file_path)
    except:
        img_logger.error(traceback.format_exc())
        return False
    else:
        return True


def main():
    success_counter = 0
    fail_counter = 0
    with ThreadPoolExecutor(max_workers=25) as executor:
        for status in executor.map(process_image, get_unfinished_images()):
            if status:
                success_counter += 1
            else:
                fail_counter += 1
    img_logger.info("多线程爬取图片，成功-{}，失败-{}".format(success_counter, fail_counter))


if __name__ == "__main__":
    main()
    while True:
        time.sleep(10 * 60)
        main()
