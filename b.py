import os, json, re, requests

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 12; 22021211RC Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.135 Mobile Safari/537.36",
    "Host": "www.kuaidaili.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "sec-ch-ua": "'Chromium';v='134', 'Not:A-Brand';v='24', 'Android WebView';v='134'",
}
session = requests.session()
session.headers.update(headers)

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

url = "https://www.kuaidaili.com/free/inha/1"
resp = session.get(url)
resp.encoding = resp.apparent_encoding

if resp.ok:
    s = fromJson(resp.text)
    if s:
        for t in s:
            if not 'ip' in t or not 'port' in t: continue
            u = t.get('ip', "") + ":" + t.get('port', "")
            print(u)