import datetime
import tkinter as tk
from tkinter import Menu, messagebox, ttk
from config import Config, __version__
from thread import QueryThread
import utils
import cli

class App:
    def __init__(self, master):
        # 初始化主应用窗口
        self.master = master
        self.master.title("Hostip")
        self.master.iconbitmap(utils.path('icon.ico'))
        self.master.geometry("820x600")
        self.master.minsize(820, 600)
        self.is_querying = False
        
        # 读取配置文件，如果不存在则使用默认值
        self.config = Config()

        # 初始化应用界面
        self.init_widgets()

    def init_widgets(self):
        # 创建主界面框架
        frame = ttk.Frame(self.master, padding=10)
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        frame.grid_rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(4, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # 创建应用界面部件
        self.create_widgets(frame)

    def create_widgets(self, frame):
        # 创建输入、查询和结果部分
        self.create_input_section(frame)
        self.create_results_section(frame)
        self.create_input_menu_section(frame)
        self.create_status_section()

    def create_input_section(self, frame):
        # 创建输入域名的标签
        label_input = ttk.Label(frame, text=f"批量输入域名，每行输入一个，最多支持{self.config.max_domain_count}个域名批量查询")
        label_input.grid(row=0, column=0, columnspan=3, sticky=tk.W)

        # 创建输入域名的文本框
        self.text_domains = tk.Text(frame, wrap=None, undo=True)
        self.text_domains.insert(1.0, self.config.default_input_domains)
        self.text_domains.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)
        self.text_domains.bind("<<Modified>>", self.on_text_domains_changed)
        self.text_domains.bind("<KeyRelease>", self.on_text_domains_changed)
        self.text_domains.bind("<<Selection>>", self.on_text_selected)
        
        # 创建输入域名文本框的滚动条
        scrollbar_domains = tk.Scrollbar(frame, command=self.text_domains.yview)
        scrollbar_domains.grid(row=1, column=3, padx=(0,10), sticky=tk.NS)
        self.text_domains.config(yscrollcommand=scrollbar_domains.set)

        # 显示输入的域名数量
        self.label_domains = ttk.Label(frame, text="0 个域名")
        self.label_domains.grid(row=2, column=0, sticky=tk.W)

        # 创建重置按钮
        button_reset = ttk.Button(frame, text="重置", command=self.on_reset_click)
        button_reset.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)

        # 创建查询按钮
        self.button_query = ttk.Button(frame, text="查询", command=self.on_query_click, state=tk.DISABLED)
        self.button_query.grid(row=2, column=2, padx=10, pady=10, sticky=tk.E)

    def create_results_section(self, frame):
        # 创建结果显示的标签
        label_results = ttk.Label(frame, text="Hosts IP-域名")
        label_results.grid(row=0, column=4, columnspan=3, padx=(10,0), sticky=tk.W)

        # 创建显示查询结果的文本框
        self.text_ips = tk.Text(frame, wrap=None, name='text_ips', undo=True)
        self.text_ips.grid(row=1, column=4, columnspan=3, padx=(10,0), sticky=tk.NSEW)
        self.text_ips.bind("<<Modified>>", self.on_text_ips_changed)
        self.text_ips.bind("<KeyRelease>", self.on_text_ips_changed)
        self.text_ips.config(tabs=(150,))

        # 创建查询结果文本框的滚动条
        scrollbar_ips = tk.Scrollbar(frame, command=self.text_ips.yview)
        scrollbar_ips.grid(row=1, column=7, padx=0, sticky=tk.NS)
        self.text_ips.config(yscrollcommand=scrollbar_ips.set)

         # 显示查询结果的IP-域名数量
        self.label_ip_domains = ttk.Label(frame, text="0 个IP-域名")
        self.label_ip_domains.grid(row=2, column=4, padx=(10,0), sticky=tk.E)

        # 创建更新Hosts按钮
        self.button_update_host = ttk.Button(frame, text="更新Hosts", command=self.on_update_host_click, state=tk.DISABLED)
        self.button_update_host.grid(row=2, column=5, padx=10, pady=10, sticky=tk.E)

        # 创建打开Hosts按钮
        button_open_host = ttk.Button(frame, text="打开Hosts", command=self.on_open_host_click)
        button_open_host.grid(row=2, column=6, padx=10, pady=10, sticky=tk.E)

    def create_input_menu_section(self, frame):
        # 创建文本域的右键菜单
        self.context_menu = tk.Menu(frame, tearoff=0)
        self.context_menu.add_command(label="撤销", command=self.undo)
        self.context_menu.add_command(label="恢复", command=self.redo)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="剪切", command=self.cut, state=tk.DISABLED)
        self.context_menu.add_command(label="复制", command=self.copy, state=tk.DISABLED)
        self.context_menu.add_command(label="粘贴", command=self.paste)
        self.context_menu.add_command(label="删除", command=self.delete, state=tk.DISABLED)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="全选", command=self.select_all)
        self.text_domains.bind("<Button-3>", self.show_context_menu)

    def create_status_section(self):
        # 创建状态栏
        self.status_bar = tk.Label(self.master, text="就绪", bd=00, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, padx=10, pady=(0,3), sticky="ew")
        # 版本号
        version_label = tk.Label(self.master, text=f'版本号: {__version__}', anchor=tk.E)
        version_label.grid(row=1, column=0, padx=10, pady=(0,3), sticky="e")

    def get_domains(self):
        # 获取输入的域名列表
        return [domain.strip() for domain in self.text_domains.get(1.0, tk.END).strip().splitlines() if domain.strip()]
        
    def get_valid_domains(self):
        # 获取有效的域名列表
        domains = self.get_domains()
        return [domain for domain in domains if utils.is_valid_domain(domain)]

    def on_text_domains_changed(self, event):
        # 处理输入域名文本框内容变化事件
        self.text_domains.tag_remove("highlight", "1.0", tk.END)
        domains = self.get_domains()
        # 过滤掉非法域名
        valid_domains = [domain for domain in domains if utils.is_valid_domain(domain)]
        invalid_domains_count = len(domains) - len(valid_domains)
        label_text = f'{len(domains)} 个域名'
        if invalid_domains_count:
            label_text += f'（{invalid_domains_count} 个域名无效）'
            self.highlight_invalid_domains(domains)
        self.label_domains.config(text=label_text)
        if valid_domains and len(valid_domains) <= self.config.max_domain_count:
            self.button_query.config(state=tk.NORMAL)
        else:
            self.button_query.config(state=tk.DISABLED)

    def on_text_ips_changed(self, event):
        # 处理查询结果文本框内容变化事件
        self.text_ips.tag_remove("highlight", "1.0", tk.END)
        line_ips = self.text_ips.get(1.0, tk.END).strip().splitlines()
        ip_domains = [ip.strip() for ip in line_ips if ip.strip() and not ip.startswith('#')]
        # 过滤掉非法IP-域名
        valid_ip_domains = [ip_domain for ip_domain in ip_domains if utils.is_valid_ip_domain(ip_domain)]
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
        # 处理重置按钮点击事件
        self.text_domains.delete(1.0, tk.END)
        self.text_domains.insert(1.0, self.config.default_input_domains)
        self.text_domains.event_generate("<<Modified>>")

    def on_query_click(self):
        # 处理查询按钮点击事件
        if self.is_querying:
            status_bar_text = self.status_bar.cget('text')
            self.update_status_bar(status_bar_text + '请稍候……')
            return

        self.is_querying = True
        self.start_time = datetime.datetime.now()
        valid_domains = self.get_valid_domains()
        if valid_domains:
            self.update_status_bar('查询中，请稍候……')
            query_thread = QueryThread(self, valid_domains)
            query_thread.daemon = True
            query_thread.start()

    def on_query_callback(self, domain_ips):
        # 处理查询回调事件
        self.is_querying = False
        current_time = datetime.datetime.now()
        if domain_ips:
            ips_domains = [f"{ip_address}\t{domain}" for domain, ip_address in domain_ips.items()]
            host_ips = "\r\n".join(ips_domains)

            host_context = f"""# Hostip Host Start
# {list(domain_ips.keys())[0]} {len(ips_domains)} domain IP addresses
{host_ips}
# Update time: {current_time}
# Hostip Host End"""
        else:
            host_context = f'# 没有查询到结果'

        self.text_ips_insert(host_context)
        usedTime = current_time - self.start_time
        self.update_status_bar(f"查询用时 {usedTime.total_seconds()} 秒")

    def on_query_exception_callback(self, error_message):
        self.is_querying = False
        self.update_status_bar(error_message)
        messagebox.showerror("错误", error_message)

    def text_ips_insert(self, context):
        # 插入查询结果到文本框
        text_ips = self.master.winfo_toplevel().winfo_children()[0].children['text_ips']
        text_ips.delete(1.0, tk.END)
        text_ips.insert(1.0, context)
        text_ips.event_generate("<<Modified>>")

    def on_update_host_click(self):
        # 处理更新Hosts按钮点击事件
        answer_yes = messagebox.askyesno("确认", "你确定要执行此操作吗？")
        if answer_yes:
            host_context = self.text_ips.get(1.0, tk.END).strip()

            self.update_status_bar('正在更新Hosts……')
            utils.update_hosts_file(host_context)
            self.update_status_bar('更新完成')
            messagebox.showinfo("提示", "更新完成")

    def on_open_host_click(self):
        # 处理打开Hosts按钮点击事件
        utils.open_hosts_file()

    def update_status_bar(self, text):
        # 更新状态栏文本
        self.status_bar.config(text=text)

    def highlight_text(self, text_widget, start_index, end_index):
        # 高亮显示文本
        text_widget.tag_add("highlight", start_index, end_index)
        text_widget.tag_config("highlight", background="yellow")
    
    def highlight_invalid_domains(self, domains):
        # 高亮显示无效的域名
        for i, line in enumerate(self.text_domains.get(1.0, tk.END).splitlines()):
            if not utils.is_valid_domain(line.strip()):
                start_index = f'{i + 1}.0'
                end_index = f'{i + 1}.{len(line)}'
                self.highlight_text(self.text_domains, start_index, end_index)
    
    def highlight_invalid_ip_domains(self, domains):
        # 高亮显示无效的IP-域名
        for i, line in enumerate(self.text_ips.get(1.0, tk.END).splitlines()):
            if not line.startswith('#') and not utils.is_valid_ip_domain(line.strip()):
                start_index = f'{i + 1}.0'
                end_index = f'{i + 1}.{len(line)}'
                self.highlight_text(self.text_ips, start_index, end_index)

    def show_context_menu(self, event):
        # 保存选中的文本范围
        sel_ranges = self.text_domains.tag_ranges("sel")

        # 更新撤销和恢复按钮状态
        self.update_undo_redo_buttons()

        # 恢复选中的文本范围
        for start, end in zip(sel_ranges[::2], sel_ranges[1::2]):
            self.text_domains.tag_add(tk.SEL, start, end)

        # 弹出右键菜单
        self.context_menu.post(event.x_root, event.y_root)

    def update_undo_redo_buttons(self):
        # 更新撤销和恢复按钮状态
        if self.is_undoable():
            self.context_menu.entryconfig("撤销", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("撤销", state=tk.DISABLED)

        if self.is_redoable():
            self.context_menu.entryconfig("恢复", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("恢复", state=tk.DISABLED)

    def is_undoable(self):
        # 判断是否可撤销
        try:
            self.text_domains.edit_undo()
            self.text_domains.edit_redo()
            return True
        except tk.TclError:
            return False

    def is_redoable(self):
        # 判断是否可恢复
        try:
            self.text_domains.edit_redo()
            self.text_domains.edit_undo()
            return True
        except tk.TclError:
            return False

    def undo(self):
        # 执行撤销操作
        try:
            self.text_domains.edit_undo()
            self.text_domains.event_generate("<<Modified>>")
        except tk.TclError:
            pass

    def redo(self):
        # 执行恢复操作
        try:
            self.text_domains.edit_redo()
            self.text_domains.event_generate("<<Modified>>")
        except tk.TclError:
            pass

    def cut(self):
        # 执行剪切操作
        if self.text_domains.tag_ranges("sel"):
            self.text_domains.event_generate("<<Cut>>")
            self.text_domains.event_generate("<<Modified>>")

    def copy(self):
        # 执行复制操作
        self.text_domains.event_generate("<<Copy>>")

    def paste(self):
        # 执行粘贴操作
        self.text_domains.event_generate("<<Paste>>")
        self.text_domains.event_generate("<<Modified>>")

    def delete(self):
        # 执行删除操作
        if self.text_domains.tag_ranges("sel"):
            self.text_domains.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_domains.event_generate("<<Modified>>")

    def select_all(self):
        # 执行全选操作
        self.text_domains.tag_add(tk.SEL, "1.0", tk.END)
    
    def on_text_selected(self, event):
        # 处理文本选择事件，根据选择状态更新菜单项的可用性
        if self.text_domains.tag_ranges("sel"):
            self.context_menu.entryconfig("剪切", state=tk.NORMAL)
            self.context_menu.entryconfig("复制", state=tk.NORMAL)
            self.context_menu.entryconfig("删除", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("剪切", state=tk.DISABLED)
            self.context_menu.entryconfig("复制", state=tk.DISABLED)
            self.context_menu.entryconfig("删除", state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    if cli.main(True):
        main()

# 执行这个命令生成exe文件
# pyinstaller -F main.py -n Hostip --add-data 'icon.ico;.' -i icon.ico -w