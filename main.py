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

def first_url(text):
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
            if os.system(f'git add "{DOMAIN_FILE}" >/dev/null 2>&1') == 0:
                os.system('git commit -m "更新" >/dev/null 2>&1')
                os.system('git push --quiet --force-with-lease')
        except Exception as e:
            return False
        return True
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
    print(saved_domain)
    if saved_domain:
        target_url = f"http://{saved_domain}/go.js"
        try:
            resp = session.get(target_url)
            resp.encoding = resp.apparent_encoding
            if resp.status_code == 200:
                url = first_url(resp.text)
                if url and is_valid_url(url):
                    resp = session.get(url)
                    resp.encoding = resp.apparent_encoding
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        flash_text = soup.select_one('p.flash-text')
                        if flash_text:
                            new_domain = first_domain(flash_text.text)
                            if new_domain and is_valid_domain(new_domain) and new_domain != saved_domain:
                                return save_domain(new_domain)
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except Exception as e:
            return None
    else:
        return None

if __name__ == "__main__":
    final_domain = process_domain_workflow()
    print(final_domain)
    if final_domain:
        print(f"成功提取域名: {final_domain}")
    else:
        exit(1)