import requests
from bs4 import BeautifulSoup

def batch_query(domains):
    url = "https://ip.tool.chinaz.com/ipbatch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = {
        "ips": "\r\n".join(domains),
        'submore': '查询'
    }

    with requests.Session() as session:
        response = session.post(url, headers=headers, data=data)

    ip_addresses = {}
    soup = BeautifulSoup(response.text, "html.parser")
    for row in soup.select("table.WhoIpWrap.trime.ww100.tc.lh30 tbody#ipList tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        ip_address = {cells[0].text.strip() : cells[1].text.strip()}
        ip_addresses.update(ip_address)
    return ip_addresses