# Readme

## 1. 示例爬取地址

### 组列表获取

https://c1.acgnavi.com:8441/index?index=mainindex&isv=0&mode=21&sign=0FC957744BC740A88F9E23F83E18E094B0C141E9A6895E9C74328106A62055A6

### 内部列表获取

https://c1.acgnavi.com:8441/index?index=promptads&mode=21&sign=88BDC991FCF242D4B3D5469FC560424FA1280511D07B925025C0B7FB4D57268F

### 单独图片获取

https://c.acgnavi.com/tuiguangacg/tSTAY_4090EDFF_0000.JPG

### 备注

参数中 isv、mode、sign 都没有实际用途

## 2. 数据结构

### key: meta

```json
[
    {
        "id": "18010142",
        "group_name": "[踊るねこ人間] MISA NOTE",
        // surface
        "origin_url": "",
        "nos_key": "",
        "nos_url": "",
        "local_file_path": "",
        "finish": true  // false
    },
    // ...
]
```

### key: 18010142

```json
[
    {
        "id": "1234567888",
        "origin_url": "https://c.acgnavi.com/tuiguangcos/tSTAY_003.JPG",
        "nos_key": "key",
        "nos_url": "https://c.acgnavi.com/tuiguangcos/tSTAY_003.JPG",
        "local_file_path": "/a/b/c/tSTAY_003.JPG",
        "file_name": "tSTAY_003.JPG",
        "finish": true  // false
    }, 
    // ...
]
```

### key: favor

```json
[
    {
        "id": "1234567888",
        "origin_url": "https://c.acgnavi.com/tuiguangcos/tSTAY_003.JPG",
        "nos_key": "key",
        "nos_url": "https://c.acgnavi.com/tuiguangcos/tSTAY_003.JPG",
        "local_file_path": "/a/b/c/tSTAY_003.JPG",
        "file_name": "tSTAY_003.JPG",
        "add_timestamp": 1234567890123,
        "group_id": "18010142"
    }, 
    // ...
]
```

## 3. 思路

### meta 信息

每天凌晨3点爬取一次，信息只增加不减少，存在 localdb 中，记录日志

### 图片

- 每五分钟检测 meta 信息中爬取未成功的图片并爬取
- 为了效率采用代理
- 多线程爬取，16 个线程，每个线程爬取间隔 1s
