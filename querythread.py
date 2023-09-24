import threading
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup

class QueryThread(threading.Thread):
    def __init__(self, app, domains):
        super().__init__()
        self.app = app
        self.domains = domains

    def run(self):
        try:
            # 执行查询操作，触发查询回调事件
            domain_ips = self.batch_query(self.domains)
            self.app.on_query_callback(domain_ips)
        except requests.RequestException as e:
            self.handle_request_exception(e)
        except Exception as e:
            self.handle_other_exception(e)

    def handle_request_exception(self, exception):
        self.app.is_querying = False
        error_message = f'网络请求出错。{str(exception)}'
        self.app.update_status_bar(error_message)
        messagebox.showerror("错误", error_message)

    def handle_other_exception(self, exception):
        self.app.is_querying = False
        error_message = f'出错了。{str(exception)}'
        self.app.update_status_bar(error_message)
        messagebox.showerror("错误", error_message)

    def batch_query(self, domains):        
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