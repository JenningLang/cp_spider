import os

import oss2

from config import ACCESS_KET_ID, ACCESS_KEY_SECRET, BUCKET_NAME, DEV
if DEV:
    from config import OUTER_ENDPOINT as ENDPOINT
else:
    from config import INNER_ENDPOINT as ENDPOINT


bucket = oss2.Bucket(
    oss2.Auth(ACCESS_KET_ID, ACCESS_KEY_SECRET), ENDPOINT, BUCKET_NAME
)


# # # # # 统一约定文件存储为 姓名/图片名称

def put_image(img_path, group_name=""):
    """
    向 oss 中存入图像
    :param img_path: 文件本地路径，包含名称
    :param group_name: 为一组照片的组名
    :return: 存储 key 值, 存储是否成功
    """
    img_name = os.path.split(img_path)[-1]
    key = "{}/{}/{}".format(
        BUCKET_NAME, group_name, img_name
    )  # oss 中标识符
    put_res = bucket.put_object_from_file(
        key=key, filename=img_path
    )
    return key, put_res


def get_image(save_path, key):
    """
    从 oss 下载图像
    下载后完整的文件名为: save_path/prefix/img_name
    :param save_path:  文件存储路径
    :param key:  oss 中文件标识符
    :return: 下载后本地路径, 下载是否成功
    """
    group_name, img_name = key.split("/")[1:]  # 从 key 中分离专辑名和文件名
    file_path = os.path.join(save_path, group_name)  # 文件保存路径
    file_path_name = os.path.join(file_path, img_name)  # 文件保存路径 + 名称
    os.makedirs(file_path, exist_ok=True)  # 预防文件不存在
    get_res = bucket.get_object_to_file(
        key=key, filename=file_path_name
    )
    return file_path_name, get_res


def main():
    res = put_image(
        img_path="./data/test_img.jpg", group_name="test"
    )
    print("put image result: ", res)
    res = get_image(
        save_path="./data", key="simple-server-data/test/test_img.jpg"
    )
    print("put image result: ", res)


if __name__ == "__main__":
    main()