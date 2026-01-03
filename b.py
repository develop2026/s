import os, json, re, requests, ipaddress, time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

ips = set()
jips = set()
successful_proxies = []

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

def load():
    fileName = "ips.txt"
    try:
        with open(fileName, "r", encoding="utf-8") as f:
            for line in f:
                ip = line.strip()
                if ":" not in ip or not ip: continue
                newIp, newPort = ip.split(':', 1)
                if not validate_ip_port(newIp, newPort): continue
                jips.add(ip)
    except Exception as e:
        pass

def verify(proxy):
    target_url = 'https://www.zdaye.com/free/?ip=&adr=&checktime=&sleep=&cunhuo=&dengji=&protocol=http&https=1&yys=&post=&px='
    proxies = {
        'https': f'http://{proxy}',
        'http': f'http://{proxy}'
    }
    start_time = time.time()
    try:
        response = requests.get(target_url, headers=headers, proxies=proxies, timeout=10)
        return proxy, response.ok, int((time.time() - start_time) * 1000)
    except:
        return proxy, False, -1

def v():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(verify, proxy) for proxy in jips]
        for future in as_completed(futures):
            proxy, is_valid, requestTime = future.result()
            if is_valid:
                successful_proxies.append((proxy, requestTime))
    successful_proxies.sort(key=lambda x: x[1])

def pac(proxies = {}):
    proxy = "39.105.102.234:8080"
    proxies = {
        'https': f'http://{proxy}',
        'http': f'http://{proxy}'
    }
    url = "https://www.zdaye.com/free/?ip=&adr=&checktime=&sleep=&cunhuo=&dengji=&protocol=http&https=1&yys=&post=&px="
    if proxies:
        resp = requests.get(url,headers=headers, proxies=proxies, timeout=10)
    else:
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

pac()
if ips:
    save()
else:
    load()
    v()
    for proxy, req_time in successful_proxies:
        print(f"{proxy} - {req_time}ms")
        pac()
        if ips:
            save() 
            break