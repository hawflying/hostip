import threading
import requests
import request_util

class QueryThread(threading.Thread):
    def __init__(self, app, domains):
        super().__init__()
        self.app = app
        self.domains = domains

    def run(self):
        try:
            # 执行查询操作，触发查询回调事件
            domain_ips = request_util.batch_query(self.domains)
            self.app.on_query_callback(domain_ips)
        except requests.RequestException as e:
            self.handle_request_exception(e)
        except Exception as e:
            self.handle_other_exception(e)

    def handle_request_exception(self, exception):
        error_message = f'网络请求出错。{str(exception)}'
        self.app.on_query_exception_callback(error_message)

    def handle_other_exception(self, exception):
        error_message = f'出错了。{str(exception)}'
        self.app.on_query_exception_callback(error_message)