from requests_html import HTMLSession

session = HTMLSession()
r = session.get("https://baidu.com")

cookies = session.cookies.get_dict()
print(cookies)

