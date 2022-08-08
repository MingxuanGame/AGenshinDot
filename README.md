# AGenshinDot

[![PyPI](https://img.shields.io/pypi/v/agenshindot?style=flat-square)](https://pypi.org/project/agenshindot)
[![Python Version](https://img.shields.io/pypi/pyversions/agenshindot?style=flat-square)](https://pypi.org/project/agenshindot)
[![License](https://img.shields.io/github/license/MingxuanGame/AGenshinDot?style=flat-square)](https://github.com/MingxuanGame/AGenshinDot/blob/master/LICENSE)
[![QQ群](https://img.shields.io/badge/QQ%E7%BE%A4-929275476-success?style=flat-square)](https://jq.qq.com/?_wv=1027&k=C7XY04F1)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/MingxuanGame/AGenshinDot/master.svg)](https://results.pre-commit.ci/latest/github/MingxuanGame/AGenshinDot/master)

AGenshinDot 是 [GenshinDot](https://github.com/MingxuanGame/GenshinDot) 的 Python 实现，由 [Graia-Ariadne](https://github.com/GraiaProject/Ariadne) 驱动.

## 声明

AGenshinDot 遵循 `AGPLv3` 许可协议开放全部源代码，你可在[这里](./LICENSE)找到本项目的许可证.

AGenshinDot 仅供学习娱乐使用，禁止将此 Bot 用于商用和非法用途.

AGenshinDot 项目及作者不对因使用本项目所造成的损失进行赔偿，也不承担任何法律责任.

## 安装

### 从 PyPI 安装

```bash
pip install agenshindot
# or
poetry add agenshindot
```

### 从 GitHub 安装

1.直接安装

```bash
poetry add git+https://github.com/MingxuanGame/AGenshinDot.git
```

2.克隆后安装

```bash
git clone https://github.com/MingxuanGame/AGenshinDot.git
cd AGenshinDot
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
# 是否启用控制台
enable_console = false
# 是否开启 Cookie 绑定
enable_bind_cookie = false
# 机器人管理员 QQ 号
admins = [1060148379]

# 以下为连接配置
# 如果不配置则默认为 HTTP + 正向 WebSocket，连接地址为 localhost:8080
# 可以同时配置多种连接

# 正向 WebSocket 配置
ws = "ws://localhost:8080"
# 等同于如下配置
# ws = ["ws://localhost:8080"]

# HTTP 配置
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

# 日志配置
[log]
# 日志等级，详情请看 loguru 文档
level = "INFO"
# 过期时间，过期的日志将被删除，格式请看 
# https://pydantic-docs.helpmanual.io/usage/types/#datetime-types
# 中 `timedelta` 部分
expire_time = "P14DT0H0M0S"
# 是否启用数据库日志
db_log = false
```

## 启动

1.执行本项目文件夹下的 `bot.py`

```bash
python bot.py
```

2.以模块形式启动

```bash
python -m agenshindot
```

## 控制台命令

> WARNING
> 控制台属于实验性内容，不建议使用
>
>启用控制台后，会禁用标准输出中 **日志等级** 的设置

在启用控制台后，可以输入以下命令执行一些操作

* `/stop`

  关闭 AGenshinDot.

* `/license`

  输出许可证信息.

* `/version`

  输出 AGenshinDot LOGO 和版本信息.

* `/execute <SQL 语句>`

  执行 SQL 语句 **（危险操作）**
