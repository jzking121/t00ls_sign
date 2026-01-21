#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import time
import cloudscraper  # 导入 cloudscraper 替换 requests
import requests      # 保留用于 Server 酱推送（通常 API 不会被 CF 拦截）

"""
环境变量约定（用于 GitHub Actions）：

T00LS_USERNAME   -> T00ls 用户名（明文）
T00LS_PASSWORD   -> T00ls 登录密码的 32位小写MD5 值（不是明文密码）
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



# 读取环境变量
username = os.getenv("T00LS_USERNAME", "").strip()
password = os.getenv("T00LS_PASSWORD", "").strip()
questionid_str = os.getenv("T00LS_QID", "").strip()
answer = os.getenv("T00LS_QANS", "").strip()
server_sendkey = os.getenv("T00LS_SCKEY", "").strip()

try:
    questionid = int(questionid_str) if questionid_str else 0
except ValueError:
    questionid = 0

# 初始化 cloudscraper 实例
scraper = cloudscraper.create_scraper()
scraper.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.t00ls.com/members-profile.html"
})

def server_wx(title, desp):
    """Server酱微信推送"""
    if not server_sendkey:
        print("未配置 Server 酱 SendKey，跳过微信推送。")
        return
    url = f"https://sctapi.ftqq.com/{server_sendkey}.send"
    data = {"title": title, "desp": desp}
    try:
        # 推送通常使用标准 requests 即可
        resp = requests.post(url=url, data=data, timeout=10)
        print("Server酱返回：", resp.text)
    except Exception as e:
        print("调用 Server酱 推送失败：", e)

def login():
    """T00ls 登录接口，返回 formhash"""
    if not username or not password:
        raise ValueError("环境变量未配置完整，请检查：T00LS_USERNAME / T00LS_PASSWORD")

    url = "https://www.t00ls.com/login.json"
    param = {
        "action": "login",
        "username": username,
        "password": password,
        "questionid": questionid,
        "answer": answer
    }

    print(f"开始登录 T00ls 用户: {username} ...")
    # 使用 scraper 绕过 CF
    response = scraper.post(url=url, data=param, timeout=20)
    
    if "<title>Attention Required! | Cloudflare</title>" in response.text:
        raise Exception("登录请求被 Cloudflare 拦截，即使使用了 cloudscraper 也未能绕过。")

    try:
        rjson = response.json()
    except Exception:
        print("登录接口返回内容不是 JSON：", response.text[:500])
        raise

    print("登录返回：", rjson)

    if rjson.get("status") != "success" or "formhash" not in rjson:
        msg = rjson.get("message", "登录失败，返回中没有 formhash 字段")
        raise ValueError(f"登录失败：{msg}")

    return rjson["formhash"]

def sign_in(formhash):
    """T00ls 签到接口"""
    login_url = "https://www.t00ls.com/ajax-sign.json"
    param = {
        "formhash": formhash,
        "signsubmit": "true" # 对应原逻辑，2.py 中是 'apply'，通常 true 或 apply 均可
    }
    print("开始签到 ...")
    # scraper 会自动处理 Cookie
    response = scraper.post(url=login_url, data=param, timeout=20)
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
        # 增加一点随机延迟，模拟真实行为
        time.sleep(2)
        result = json.loads(sign_in(formhash))
    except Exception as e:
        title = "T00ls签到失败（解析返回）"
        msg = f"签到返回解析异常：{e}"
        print(msg)
        server_wx(title, msg)
        return

    # 根据返回状态判断成功与否
    status = result.get("status", "")
    message = result.get("message", "")
    
    if status == "success":
        title = "T00ls签到成功"
    elif "alreadysign" in str(message) or "已签到" in str(message):
        title = "T00ls今日已签到"
    else:
        title = "T00ls签到失败"

    msg = f"签到结果: {message}"
    server_wx(title, msg)
    print(f"标题: {title}\n详情: {msg}")

def main_handler(event, context):
    main()
    return "签到完毕"

if __name__ == "__main__":
    main()
