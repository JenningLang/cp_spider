import time
import json

from django.shortcuts import render
from django.http import JsonResponse


from config import META_KEY
from util import get_redis_cli

ROW_SIZE = 3


def render_default_index(request):
    meta_data = group_data(get_global_meta_from_redis(), group_size=3)
    row_idx = range(10)  # 默认先展示十行

    max_row_num = len(meta_data) // ROW_SIZE

    return render(
        request, "index.html",
        {
            "meta_data": [
                {
                    "name": idx,
                    "data": meta_data[int(idx)]
                } for idx in row_idx
            ],
            "row_list": range(0, max_row_num + 1),
            "next_row_idx": 10
        }
    )


def get_index_data(request):
    ret_len = 5
    req_id = int(request.GET["id"])
    meta_data = group_data(get_global_meta_from_redis(), group_size=3)
    return JsonResponse({
        "next_row_idx": req_id + ret_len,
        "meta_data": [
            {
                "name": idx,
                "data": meta_data[int(idx)]
            } for idx in range(req_id, req_id + ret_len)
        ],
    })


def render_default_group(request):
    group_id = request.GET["id"]
    group_meta = group_data(
        get_group_meta_from_redis(group_id=group_id),
        group_size=3
    )
    row_idx = range(10)  # 默认先展示十行

    max_row_num = len(group_meta)
    print(len(group_meta))
    return render(
        request, "group.html",
        {
            "id": group_id,
            "meta_data": [
                {
                    "name": idx,
                    "data": group_meta[int(idx)]
                } for idx in row_idx if idx < len(group_meta)
            ],
            "row_list": range(0, max_row_num + 1),
            "next_row_idx": 10
        }
    )


def get_group_data(request):
    ret_len = 5
    req_id = int(request.GET["id"])
    group_id = request.GET["group_id"]
    group_meta = group_data(
        get_group_meta_from_redis(group_id=group_id),
        group_size=3
    )
    if req_id + ret_len >= len(group_meta):
        next_row_idx = -2
    else:
        next_row_idx = req_id + ret_len

    return JsonResponse({
        "next_row_idx": next_row_idx,
        "meta_data": [
            {
                "name": idx,
                "data": group_meta[idx]
            } for idx in range(req_id, req_id + ret_len) if idx < len(group_meta)
        ],
    })


# ----- Util ----- #
_meta_data = None
_meta_last_load_time = None


def get_global_meta_from_redis():
    global _meta_data, _meta_last_load_time
    reload = False
    if _meta_data is None or _meta_last_load_time is None:
        reload = True
    elif time.time() > _meta_last_load_time + 10 * 60:  # 10 minute
        reload = True
    if reload:
        _meta_data = json.loads(get_redis_cli().get(META_KEY).decode("utf8"))
        _meta_last_load_time = time.time()
    return _meta_data


def get_group_meta_from_redis(group_id):
    group_key = "group:{}".format(group_id)
    group_meta = json.loads(get_redis_cli().get(group_key).decode("utf8"))
    return group_meta


def group_data(data, group_size=3):
    return [
        data[i: i + group_size] for i in range(0, len(data), group_size)
    ]
