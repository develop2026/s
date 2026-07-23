import requests
import re
import os
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 12; 22021211RC Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.135 Mobile Safari/537.36",
}
session = requests.session()
session.headers.update(headers)

DOMAIN_FILE = "domain.txt"

def is_valid_url(url):
    if not url:
        return False
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(url_pattern, url))

def is_valid_domain(domain):
    if not domain:
        return False
    pattern = r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    if re.match(pattern, domain):
        if '..' in domain or domain.startswith('-') or domain.endswith('-'):
            return False
        return True
    return False

def first_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('p', class_='flash-text')
    script_text = tag.script.string
    print("JS代码:", script_text.strip())
    domain = tag.script.next_sibling.strip()
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'
    return domain

def first_url2(text):
    pattern = r'["\'](https?://[^\s/$.?#].[^\s]*)["\']'
    match = re.search(pattern, text)
    if match:
        url = match.group(1)
        return url
    else:
        return text

def first_domain(text):
    pattern = r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b'
    match = re.search(pattern, text)
    if match:
        d = match.group(0)
        return d
    else:
        return text

def save_domain(domain):
    try:
        with open(DOMAIN_FILE, 'w', encoding='utf-8') as f:
            f.write(domain)
        try:
            os.system('git config --local user.name "github-actions[bot]" >/dev/null 2>&1')
            os.system('git config --local user.email "github-actions[bot]@users.noreply.github.com" >/dev/null 2>&1')
            if os.system(f'git add {DOMAIN_FILE} >/dev/null 2>&1') == 0:
                os.system('git commit -m "更新" >/dev/null 2>&1')
                os.system('git pull --quiet --rebase')
                os.system('git push --quiet --force-with-lease')
        except Exception as e:
            return False
        return domain
    except Exception as e:
        return False

def load_domain():
    try:
        if os.path.exists(DOMAIN_FILE):
            with open(DOMAIN_FILE, 'r', encoding='utf-8') as f:
                domain = f.read().strip()
                if domain and is_valid_domain(domain):
                    return domain
                else:
                    return None
        else:
            return None
    except Exception as e:
        return None

def process_domain_workflow():
    saved_domain = load_domain()
    if not saved_domain:
        return False, "未找到已保存的域名"

    target_url = f"http://{saved_domain}/go.js"

    try:
        # 第一步：请求 go.js
        resp = session.get(target_url, timeout=10)
        resp.encoding = resp.apparent_encoding

        if resp.status_code != 200:
            return False, f"请求 go.js 失败，状态码: {resp.status_code}"

        url = first_url(resp.text)
        if not url or not is_valid_url(url):
            return False, f"go.js 中未解析到有效 URL {url}"

        # 第二步：请求解析到的真实地址
        resp = session.get(url, timeout=10)
        resp.encoding = resp.apparent_encoding

        if resp.status_code != 200:
            return False, f"请求目标页面失败，状态码: {resp.status_code}"

        soup = BeautifulSoup(resp.text, 'html.parser')
        flash_text = soup.select_one('p.flash-text')
        if not flash_text:
            return False, "页面中未找到 p.flash-text 元素"

        new_domain = first_domain(flash_text.text)
        if not new_domain or not is_valid_domain(new_domain):
            return False, "flash-text 中未解析到合法域名"

        if not save_domain(new_domain):
            return False, "新域名解析成功，但保存失败"

        return True, new_domain

    except requests.exceptions.Timeout:
        return False, "请求超时"
    except requests.exceptions.RequestException as e:
        return False, f"网络请求异常: {e}"
    except Exception as e:
        return False, f"未知错误: {e}"


if __name__ == "__main__":
    state,data = process_domain_workflow()
    if state:
        print("成功提取域名:", data)
    else:
        print("失败原因:", data)
        exit(1)