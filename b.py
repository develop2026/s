import os, json, re, requests, ipaddress, time
from bs4 import BeautifulSoup

ips = set()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Android WebView";v="134"',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Host': 'www.zdaye.com'
}

def validate_ip_port(ip, port):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_multicast or ip_obj.is_unspecified:
            return False
    except ValueError:
        return False
    ip_parts = ip.split('.')
    for part in ip_parts:
        if not 0 <= int(part) <= 255:
            return False
    if not 1 <= int(port) <= 65535:
        return False
    return True

def save():
    fileName = "ips.txt"
    try:
        with open(fileName, "w", encoding="utf-8") as f:
            f.write("\n".join(ips))
        try:
            os.system('git config --local user.name "github-actions[bot]" >/dev/null 2>&1')
            os.system('git config --local user.email "github-actions[bot]@users.noreply.github.com" >/dev/null 2>&1')
            if os.system(f'git add "{fileName}" >/dev/null 2>&1') == 0:
                os.system('git commit -m "更新" >/dev/null 2>&1')
                os.system('git push --quiet --force-with-lease')
        except Exception as e:
            pass
    except Exception as e:
        pass

proxy = "39.105.102.234:8080"
proxies = {
    'https': f'http://{proxy}',
    'http': f'http://{proxy}'
}
url = "https://www.zdaye.com/free/?ip=&adr=&checktime=&sleep=&cunhuo=&dengji=&protocol=http&https=1&yys=&post=&px="
#resp = requests.get(url,headers=headers, proxies=proxies, timeout=10)
resp = requests.get(url,headers=headers, timeout=10)
resp.encoding=resp.apparent_encoding
if resp.ok:
    soup = BeautifulSoup(resp.text,'html.parser')
    trs = soup.tbody.find_all('tr')
    for tr in trs:
        v = tr.find_all('td')
        if len(v) >= 3:
            ip = v[1].get_text(strip=True)
            port = v[2].get_text(strip=True)
            isIp = validate_ip_port(ip, port)
            if not isIp: continue
            newIp = f"{ip}:{port}"
            ips.add(newIp)
            print(newIp)

if ips: save()