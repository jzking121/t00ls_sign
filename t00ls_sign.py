#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import requests
import json

"""
环境变量约定（用于 GitHub Actions）：

T00LS_USERNAME   -> T00ls 用户名（明文）
T00LS_PASSWORD   -> T00ls 登录密码的 MD5 值（不是明文密码）
T00LS_QID        -> 安全提问问题 ID（数字：1~7）
T00LS_QANS       -> 安全提问答案
T00LS_SCKEY      -> Server 酱 SendKey（可选，不填则不推送）

questionid 对应关系仅供参考：
1 母亲的名字
2 爷爷的名字
3 父亲出生的城市
4 您其中一位老师的名字
5 您个人计算机的型号
6 您最喜欢的餐馆名称
7 驾驶执照的最后四位数字
"""

# 读取环境变量（GitHub Actions 中从 Secrets 注入）
username = os.getenv("T00LS_USERNAME", "").strip()
password = os.getenv("T00LS_PASSWORD", "").strip()          # 这里要求是 MD5 值
questionid_str = os.getenv("T00LS_QID", "").strip()
answer = os.getenv("T00LS_QANS", "").strip()
server_sendkey = os.getenv("T00LS_SCKEY", "").strip()

# questionid 转成 int，非法则设为 0
try:
    questionid = int(questionid_str) if questionid_str else 0
except ValueError:
    questionid = 0

# questionid 对应关系说明，仅做参考，不参与运行
# 1 母亲的名字
# 2 爷爷的名字
# 3 父亲出生的城市
# 4 您其中一位老师的名字
# 5 您个人计算机的型号
# 6 您最喜欢的餐馆名称
# 7 驾驶执照的最后四位数字


def server_wx(title, desp):
    """
    Server酱微信推送
    """
    if not server_sendkey:
        print("未配置 Server 酱 SendKey，跳过微信推送。")
        return

    url = f"https://sctapi.ftqq.com/{server_sendkey}.send"
    data = {
        "title": title,
        "desp": desp
    }
    try:
        resp = requests.post(url=url, data=data, timeout=10)
        print("Server酱返回：", resp.text)
    except Exception as e:
        print("调用 Server酱 推送失败：", e)


def login():
    """
    T00ls 登录接口，返回 formhash
    """
    if not username or not password or not questionid or not answer:
        raise ValueError("环境变量未配置完整，请检查：T00LS_USERNAME / T00LS_PASSWORD / T00LS_QID / T00LS_QANS")

    url = "https://www.t00ls.com/login.json"
    param = {
        "action": "login",
        "username": username,
        "password": password,   # 这里要求已经是 MD5
        "questionid": questionid,
        "answer": answer
    }

    print("开始登录 T00ls ...")
    response = requests.post(url=url, data=param, timeout=10)

    # 保存 Cookie 供后续请求使用
    global Cookie
    Cookie = response.cookies

    try:
        rjson = response.json()
    except Exception:
        print("登录接口返回内容不是 JSON：", response.text)
        raise

    # 简单打印一下登录结果信息
    print("登录返回：", rjson)

    # 如果登录失败，一般不会有 formhash
    if "formhash" not in rjson:
        # 尽量把 message 打出来方便查看
        msg = rjson.get("message", "登录失败，返回中没有 formhash 字段")
        raise ValueError(f"登录失败：{msg}")

    return rjson["formhash"]


def sign_in(formhash):
    """
    T00ls 签到接口
    """
    login_url = "https://www.t00ls.com/ajax-sign.json"
    param = {
        "formhash": formhash,
        "signsubmit": "true"
    }
    print("开始签到 ...")
    response = requests.post(url=login_url, data=param, cookies=Cookie, timeout=10)
    print("签到原始返回：", response.text)
    return response.text


def main():
    try:
        formhash = login()
    except Exception as e:
        title = "T00ls签到失败（登录阶段）"
        msg = f"登录异常：{e}"
        print(msg)
        server_wx(title, msg)
        return

    try:
        result = json.loads(sign_in(formhash))
    except Exception as e:
        title = "T00ls签到失败（解析返回）"
        msg = f"签到返回解析异常：{e}"
        print(msg)
        server_wx(title, msg)
        return

    # 根据返回状态判断成功与否
    if result.get("status") == "success":
        title = "T00ls签到成功"
    else:
        title = "T00ls签到失败"

    msg = "签到结果: " + str(result.get("message", "")) + "\n"

    server_wx(title, msg)
    print("title:", title)
    print("msg:", msg)


def main_handler(event, context):
    """
    云函数入口兼容（可选）
    """
    main()
    return "签到完毕"


if __name__ == "__main__":
    main()
