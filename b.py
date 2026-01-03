import os, json, re, requests, ipaddress, time

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 12; 22021211RC Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.135 Mobile Safari/537.36",
    "Host": "www.kuaidaili.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "sec-ch-ua": "'Chromium';v='134', 'Not:A-Brand';v='24', 'Android WebView';v='134'",
}
session = requests.session()
session.headers.update(headers)
ips = set()

def fromJson(text, variable_name="fpsList"):
    patterns = [
        rf'(?:const|var|let)\s+{variable_name}\s*=\s*(.*?);',
        rf'{variable_name}\s*=\s*(.*?);',
        rf'(?:const|var|let)\s+{variable_name}\s*=\s*(.*?)(?:\s|$)',
        rf'{variable_name}\s*=\s*(.*?)(?:\s|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            value_part = match.group(1).strip()
            array_match = re.search(r'(\[.*\])', value_part, re.DOTALL)
            if array_match:
                json_str = array_match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    pass
    return None

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

def pac(page):
    url = f"https://www.kuaidaili.com/free/inha/{page}"
    resp = session.get(url)
    resp.encoding = resp.apparent_encoding
    isOk = False
    if resp.ok:
        fpsList = fromJson(resp.text)
        if fpsList:
            for t in fpsList:
                if not 'ip' in t or not 'port' in t: continue
                ip = t.get('ip', "")
                port = t.get('port', "")
                isIp = validate_ip_port(ip, port)
                if not isIp: continue
                u =  f"{ip}:{port}"
                ips.add(u)
                isOk = True
    return isOk

if pac(1):
    time.sleep(2)
    pac(2)
    pass

if ips: save()