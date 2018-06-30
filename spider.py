import requests
import dbm
import os
import time
import random
import logging
from logging.handlers import TimedRotatingFileHandler


error_logger = logging.getLogger("request_logger")
formatter = logging.Formatter(
    '%(asctime)s level-%(levelname)-8s: %(message)s'
)
timed_rotating_file_handler = TimedRotatingFileHandler("./error_log", 'midnight')
timed_rotating_file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
timed_rotating_file_handler.suffix = "%Y%m%d.log"
error_logger.addHandler(timed_rotating_file_handler)
error_logger.setLevel(logging.DEBUG)

group_info_url = "https://c1.acgnavi.com:8441/index?index=mainindex&isv=0&mode=21"
sub_group_info_url = "https://c1.acgnavi.com:8441/index?index={0}&mode=21"


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content


proxy = get_proxy()


def get_and_save_image(url, file_path):
    global proxy
    try:
        res = requests.get(
            url,
            proxies={"http": "http://{}".format(proxy)}
        )
        p_file = open(file_path, 'wb')
        p_file.write(res.content)
        p_file.close()
    except Exception as e:
        print("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))
        error_logger.info("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))
        try:
            proxy = get_proxy()
            res = requests.get(
                url,
                proxies={"http": "http://{}".format(proxy)}
            )
            p_file = open(file_path, 'wb')
            p_file.write(res.content)
            p_file.close()
        except Exception as e:
            print("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))
            error_logger.info("ERROR ::: {0} ::: {1} ::: {2}".format(url, file_path, repr(e)))


def get_and_save_group_info():
    """
    1. Get group info and compare it with ones in ./data/urls/group_index
    2. if 1 has diff, save it in ./data/urls/group_index
    3. return the full index
    :return: [index]
    """
    global group_info_url
    global proxy
    db = dbm.open('group_names', 'c')
    res = requests.get(
        group_info_url,
        verify=False,
        proxies={"http": "http://{}".format(proxy)}
    )
    indexes = res.json()["indexes"]
    r_val = dict(
        [item["index"], item["des"]]
        for item in indexes
    )
    with open("./data/urls/group_index", "r") as gi_file:
        index = gi_file.readline().replace("\n", "")
        while index:
            if index not in r_val:
                try:
                    name_temp = db[index]
                except:
                    name_temp = "???{0}".format(random.random())
                r_val[index] = name_temp
            index = gi_file.readline().replace("\n", "")

    with open("./data/urls/group_index", "w") as gi_file:
        for item in r_val:
            gi_file.write("{0}\n".format(item))
            db[item] = r_val[item]
        db.close()
    return r_val


def get_and_save_details(sub_group_index, forced=False):
    db = dbm.open('group_names', 'c')
    name = db[str(sub_group_index)].decode("utf-8")
    db.close()
    file_path = "./data/image/{0}".format(name)
    if os.path.exists(file_path):
        if not forced:
            print("数据已经存在? {0} ::: {1} ::: {2}".format(
                sub_group_index, name, file_path
            ))
            return
    try:
        os.mkdir(file_path)
    except:
        pass

    global sub_group_info_url
    global proxy
    this_group_url = sub_group_info_url.format(sub_group_index)
    res = requests.get(
        this_group_url,
        verify=False,
        proxies={"http": "http://{}".format(proxy)}
    )
    indexes = res.json()["info"]
    cnt = 1
    for item in indexes:
        print("ITEM: ", cnt)
        error_logger.info("ITEM: {0}".format(cnt))
        cnt += 1
        sleep_time = 0.1 + 0.1 * random.random()
        time.sleep(sleep_time)
        image_url = str(item["url"])
        image_name = image_url
        while image_name.find("/") != -1:
            image_name = image_name[image_name.find("/") + 1:]
        image_path = file_path + "/{0}".format(image_name)
        get_and_save_image(image_url, image_path)


# get_and_save_image(
#     "https://c.acgnavi.com/tuiguangacg/tSTAY_4090EDFF_0000.JPG",
#     "test.jpg"
# )

group_info = get_and_save_group_info()
cnt = 1
for item in group_info:
    print(cnt, " ::: ", item, " ::: ", group_info[item])
    error_logger.info("{0} ::: {1} ::: {2}".format(cnt, item, group_info[item]))
    get_and_save_details(item)
    cnt += 1
