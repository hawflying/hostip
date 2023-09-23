import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import requests
from bs4 import BeautifulSoup
import datetime
import re
import os
import subprocess

default_input = """github.com
github.io
github.blog
github.community
api.github.com
gist.github.com
live.github.com
alive.github.com
central.github.com
codeload.github.com
collector.github.com
education.github.com
assets-cdn.github.com
avatars.githubusercontent.com
avatars0.githubusercontent.com
avatars1.githubusercontent.com
avatars2.githubusercontent.com
avatars3.githubusercontent.com
avatars4.githubusercontent.com
avatars5.githubusercontent.com
raw.githubusercontent.com
camo.githubusercontent.com
cloud.githubusercontent.com
media.githubusercontent.com
desktop.githubusercontent.com
favicons.githubusercontent.com
objects.githubusercontent.com
user-images.githubusercontent.com
pipelines.actions.githubusercontent.com
github-com.s3.amazonaws.com
github-cloud.s3.amazonaws.com
github-production-user-asset-6210df.s3.amazonaws.com
github-production-release-asset-2e65be.s3.amazonaws.com
github-production-repository-file-5c1aeb.s3.amazonaws.com
githubstatus.com
github.githubassets.com
github.map.fastly.net
github.global.ssl.fastly.net
vscode.dev
api.funcaptcha.com"""

def is_valid_ip(ip):
    # 使用正则表达式匹配合法的IP地址
    pattern = re.compile(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return bool(pattern.match(ip))

def is_valid_domain(domain):
    # 使用正则表达式匹配合法的域名
    pattern = re.compile(r"^([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]\.)+[a-zA-Z]{2,}$")
    return bool(pattern.match(domain))

def is_valid_ip_domain(ip_domain):
    # 使用正则表达式匹配合法的IP地址-域名
    ipdomain = ip_domain.split()
    return len(ipdomain) == 2 and is_valid_ip(ipdomain[0]) and is_valid_domain(ipdomain[1])

def batch_query_domain_ips(domains):    
    url = "https://ip.tool.chinaz.com/ipbatch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = {
        "ips": "\r\n".join(domains),
        'submore': '查询'
    }

    ip_addresses = {}
    try:
        response = requests.post(url, headers=headers, data=data)
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.select("table.WhoIpWrap.trime.ww100.tc.lh30 tbody#ipList tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            ip_address = {cells[0].text.strip() : cells[1].text.strip()}
            ip_addresses.update(ip_address)
    except Exception as e:
        app.update_status_bar(f'出错了。{e.args}')
        messagebox.showerror("错误", e.args)
    return ip_addresses

def process_query_result(domain_ips):
    current_time = datetime.datetime.now()
    if domain_ips:
        ips_domains = []
        for domain, ip_address in domain_ips.items():
            ips_domains.append(f"{ip_address}\t\t{domain}")
        host_ips = "\r\n".join(ips_domains)

        host_context = f"""# Hostip Host Start
# {list(domain_ips.keys())[0]} {len(ips_domains)} domain IP addresses
{host_ips}
# Update time: {current_time}
# Hostip Host End"""
    else:
        host_context = f'# 没有查询到结果'

    app.text_ips_insert(host_context)
    usedTime = current_time - app.start_time
    app.update_status_bar(f"查询用时 {usedTime.total_seconds()} 秒")

def batch_query_thread_run(domains):
    domain_ips = batch_query_domain_ips(domains)
    process_query_result(domain_ips)

def batch_query_thread(domains):
    app.update_status_bar("查询中，请稍等……")

    # 创建线程对象
    t = threading.Thread(target=batch_query_thread_run, args=(domains,))
    t.daemon = True
    t.start()

def path(filename):
    application_path = os.path.dirname(os.path.realpath(__file__))    
    return os.path.join(application_path, filename)

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Hostip")
        self.master.iconbitmap(path('icon.ico'))
        self.master.geometry("800x600")
        self.master.minsize(800, 600)
        # self.master.resizable(False, False)

        self.init_widgets()

    def init_widgets(self):            
        frame = ttk.Frame(self.master, padding=10)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        label_input = ttk.Label(frame, text="批量输入域名，每行输入一个，最多支持300个域名批量查询")
        label_input.grid(row=0, column=0, columnspan=3, padx=0, pady=0, sticky=tk.W)

        label_results = ttk.Label(frame, text="Hosts IP-域名")
        label_results.grid(row=0, column=4, columnspan=3, padx=(10,0), pady=0, sticky=tk.W)

        text_domains = tk.Text(frame, wrap=None, undo=True)
        text_domains.insert(1.0, default_input)
        text_domains.grid(row=1, column=0, columnspan=3, padx=0, pady=0, sticky=tk.NSEW)
        text_domains.bind("<<Modified>>", self.on_text_domains_changed)
        text_domains.bind("<KeyRelease>", self.on_text_domains_changed)
        text_domains.see(tk.END)
        scrollbar_domains = tk.Scrollbar(frame, command=text_domains.yview)
        scrollbar_domains.grid(row=1, column=3, padx=(0,10), sticky=tk.NS)
        text_domains.config(yscrollcommand=scrollbar_domains.set)

        text_ips = tk.Text(frame, wrap=None, name='text_ips', undo=True)
        text_ips.grid(row=1, column=4, columnspan=3, padx=(10,0), pady=0, sticky=tk.NSEW)
        text_ips.bind("<<Modified>>", self.on_text_ips_changed)
        text_ips.bind("<KeyRelease>", self.on_text_ips_changed)
        text_ips.see(tk.END)
        scrollbar_ips = tk.Scrollbar(frame, command=text_ips.yview)
        scrollbar_ips.grid(row=1, column=7, padx=0, sticky=tk.NS)
        text_ips.config(yscrollcommand=scrollbar_ips.set)

        label_domains = ttk.Label(frame, text="0 个域名")
        label_domains.grid(row=2, column=0, padx=0, pady=0, sticky=tk.W)

        button_reset = ttk.Button(frame, text="重置", command=self.on_reset_click)
        button_reset.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)

        button_query = ttk.Button(frame, text="查询", command=self.on_query_click, state=tk.DISABLED)
        button_query.grid(row=2, column=2, padx=10, pady=10, sticky=tk.E)

        label_ip_domains = ttk.Label(frame, text="0 个IP-域名")
        label_ip_domains.grid(row=2, column=4, padx=(10,0), pady=0, sticky=tk.E)

        button_update_host = ttk.Button(frame, text="更新Hosts", command=self.on_update_host_click, state=tk.DISABLED)
        button_update_host.grid(row=2, column=5, padx=10, pady=10, sticky=tk.E)

        button_open_host = ttk.Button(frame, text="打开Hosts", command=self.on_open_host_click)
        button_open_host.grid(row=2, column=6, padx=10, pady=10, sticky=tk.E)


        frame.grid_rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(4, weight=1)

        status_bar = tk.Label(self.master, text="就绪", bd=00, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, padx=10, pady=(0,3), sticky="ew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.text_domains = text_domains
        self.label_domains = label_domains
        self.button_query = button_query
        self.button_update_host = button_update_host
        self.text_ips = text_ips
        self.label_ip_domains = label_ip_domains
        self.status_bar = status_bar

    def highlight_text(self, text_widget, start_index, end_index):
        text_widget.tag_add("highlight", start_index, end_index)
        text_widget.tag_config("highlight", background="yellow")
    
    def highlight_invalid_domains(self, domains):
        for i, line in enumerate(self.text_domains.get(1.0, tk.END).splitlines()):
            if not is_valid_domain(line.strip()):
                start_index = f'{i + 1}.0'
                end_index = f'{i + 1}.{len(line)}'
                self.highlight_text(self.text_domains, start_index, end_index)
    
    def highlight_invalid_ip_domains(self, domains):
        for i, line in enumerate(self.text_ips.get(1.0, tk.END).splitlines()):
            if not line.startswith('#') and not is_valid_ip_domain(line.strip()):
                start_index = f'{i + 1}.0'
                end_index = f'{i + 1}.{len(line)}'
                self.highlight_text(self.text_ips, start_index, end_index)

    def on_text_domains_changed(self, event):
        self.text_domains.tag_remove("highlight", "1.0", tk.END)
        domains =[domain.strip() for domain in self.text_domains.get(1.0, tk.END).strip().splitlines() if domain.strip()]
        # 过滤掉非法域名
        valid_domains = [domain for domain in domains if is_valid_domain(domain)]
        invalid_domains_count = len(domains) - len(valid_domains)
        label_text = f'{len(domains)} 个域名'
        if invalid_domains_count:
            label_text += f'（{invalid_domains_count} 个域名无效）'
            self.highlight_invalid_domains(domains)
        self.label_domains.config(text=label_text)
        if valid_domains and len(valid_domains) <= 300:
            self.button_query.config(state=tk.NORMAL)
        else:
            self.button_query.config(state=tk.DISABLED)

    def on_text_ips_changed(self, event):
        self.text_ips.tag_remove("highlight", "1.0", tk.END)
        line_ips = self.text_ips.get(1.0, tk.END).strip().splitlines()
        ip_domains = [ip.strip() for ip in line_ips if ip.strip() and not ip.startswith('#')]
        # 过滤掉非法IP-域名
        valid_ip_domains = []
        for ip_domain in ip_domains:
            if is_valid_ip_domain(ip_domain):
                valid_ip_domains.append(ip_domain)
        invalid_ip_domains_count = len(ip_domains) - len(valid_ip_domains)
        label_text = f'{len(ip_domains)} 个IP-域名'
        if invalid_ip_domains_count:
            label_text += f'（{invalid_ip_domains_count} 个无效）'
            self.highlight_invalid_ip_domains(ip_domains)
        self.label_ip_domains.config(text=label_text)
        if valid_ip_domains:
            self.button_update_host.config(state=tk.NORMAL)
        else:
            self.button_update_host.config(state=tk.DISABLED)

    def on_reset_click(self):
        self.text_domains.delete(1.0, tk.END)
        self.text_domains.insert(1.0, default_input)
        self.on_text_domains_changed(None)

    def on_query_click(self):
        status_bar_text = self.status_bar.cget('text')
        if '查询中' in status_bar_text:
            self.update_status_bar(status_bar_text + '请稍候……')
            return

        self.start_time = datetime.datetime.now()
        domains = self.text_domains.get(1.0, tk.END).strip().splitlines()
        # 过滤掉非法域名
        valid_domains = [domain.strip() for domain in domains if is_valid_domain(domain.strip())]
        if valid_domains:
            batch_query_thread(valid_domains)

    def text_ips_insert(self, context):
        text_ips = self.master.winfo_toplevel().winfo_children()[0].children['text_ips']
        text_ips.delete(1.0, tk.END)
        text_ips.insert(1.0, context)
        self.on_text_ips_changed(None)

    def on_update_host_click(self):
        answeryes = messagebox.askyesno("确认", "你确定要执行此操作吗？")
        if answeryes:
            host_context = self.text_ips.get(1.0, tk.END).strip()

            hosts_path = os.environ['SystemRoot'] + '\\system32\\drivers\\etc\\hosts'
            # 读取host文件内容
            with open(hosts_path, 'r') as f:
                old_content = f.read()
                
            pattern = r'# Hostip Host Start.*?# Hostip Host End'
            new_content = re.sub(pattern, host_context, old_content, flags=re.DOTALL)       

            # 如果没有需要替换的内容，则直接添加到结尾
            if new_content == old_content:
                new_content = old_content + '\r\n\r\n' + host_context

            with open(hosts_path, 'w') as f:
                f.write(new_content)
            
            self.update_status_bar("Hosts文件已更新")

    def on_open_host_click(self):
        subprocess.Popen('notepad %SystemRoot%\\system32\\drivers\\etc\\hosts', shell=True)

    def update_status_bar(self, text):
        self.status_bar.config(text=text)
    

root = tk.Tk()
app = App(root)

def main():
    root.mainloop()

if __name__ == '__main__':
    main()