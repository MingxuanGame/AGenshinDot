# AGenshinDot

AGenshinDot 是 [GenshinDot](https://github.com/MingxuanGame/GenshinDot) 的 Python 实现，由 [Graia-Ariadne](https://github.com/GraiaProject/Ariadne) 驱动.

## 声明

AGenshinDot 遵循 `AGPLv3` 许可协议开放全部源代码，你可在[这里](./LICENSE)找到本项目的许可证.

AGenshinDot 仅供学习娱乐使用，禁止将此 Bot 用于商用和非法用途.

## 安装

使用 Poetry 安装.

```bash
poetry install --no-dev
```

## 配置

所有配置均保存在运行目录 `config.toml`.

下面为配置样例：

```toml
# 机器人 QQ 号
account = 1185285105
# verifyKey
verify_key = "agenshindot"

# 以下为连接配置
# 如果不配置则默认为 HTTP + 正向 WebSocket，连接地址为 localhost:8080
# 可以同时配置多种连接

# 正向 WebSocket 配置
ws = "ws://localhost:8080"
# 等同于如下配置
# ws = ["ws://localhost:8080"]

# HTTP 配置
# 正向 WebSocket 配置
http = "http://localhost:8080"
# 等同于如下配置
# http = ["http://localhost:8080"]

# 反向 WebSocket 配置
[ws_reverse]
# Endpoint
path = "/"
# 验证的参数
params = {}
# 验证的请求头
headers = {}
# WARNING 上面的配置要保证不能缺失，也不能调换位置
# 如果只需要设置 Endpoint，也可以使用下方的配置
# ws_reverse = "/"

# HTTP Webhook 配置
[webhook]
# Endpoint
path = "/"
# 验证的请求头
headers = {}
# WARNING 上面的配置要保证不能缺失，也不能调换位置
# 如果只需要设置 Endpoint，也可以使用下方的配置
# webhook = "/"
```

## 启动

1. 执行本项目文件夹下的 `bot.py`

```bash
python bot.py
```

2. 以模块形式启动

```bash
python -m agenshindot
```
