import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QLabel, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QTextOption, QIcon
from PyQt5.QtCore import Qt, pyqtSlot
from config import Config, __version__
from thread import QueryQThread
import utils
import cli

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hostip")
        self.setWindowIcon(QIcon(utils.path('icon.ico')))
        self.setGeometry(100, 100, 880, 660)
        self.setMinimumSize(800, 600)

        self.config = Config()

        self.is_querying = False
        self.start_time = None

        # 设置全局样式表来增大字体大小
        self.setStyleSheet('''
            * {
                font-size: 14px;
            }
        ''')
        self.init_widgets()

    def init_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()

        input_section = self.create_input_section()
        results_section = self.create_results_section()

        layout.addWidget(input_section)
        layout.addWidget(results_section)

        central_widget.setLayout(layout)

        self.create_status_section()

        self.on_reset_click()

    def create_input_section(self):
        input_section = QWidget()
        input_layout = QVBoxLayout()

        label_input = QLabel(f"批量输入域名，每行输入一个，最多支持{self.config.max_domain_count}个域名批量查询")
        input_layout.addWidget(label_input)

        self.text_domains = QTextEdit()
        self.text_domains.textChanged.connect(self.on_text_domains_changed)
        input_layout.addWidget(self.text_domains)

        input_info_layout = QHBoxLayout()

        self.label_domains = QLabel("0 个域名")
        input_info_layout.addWidget(self.label_domains)

        input_info_layout.addStretch(1)  # 添加弹簧，将按钮推到最右侧

        self.button_reset = QPushButton("重置")
        self.button_reset.clicked.connect(self.on_reset_click)
        input_info_layout.addWidget(self.button_reset)

        self.button_query = QPushButton("查询")
        self.button_query.setEnabled(False)
        self.button_query.clicked.connect(self.on_query_click)
        input_info_layout.addWidget(self.button_query)

        input_layout.addLayout(input_info_layout)

        input_section.setLayout(input_layout)
        return input_section

    def create_results_section(self):
        results_section = QWidget()
        results_layout = QVBoxLayout()

        label_results = QLabel("Hosts IP-域名")
        results_layout.addWidget(label_results)

        self.text_ips = QTextEdit()
        self.text_ips.textChanged.connect(self.on_text_ips_changed)
        results_layout.addWidget(self.text_ips)

        results_info_layout = QHBoxLayout()

        self.label_ip_domains = QLabel("0 个IP-域名")
        results_info_layout.addWidget(self.label_ip_domains)

        results_info_layout.addStretch(1)

        self.button_update_host = QPushButton("更新Hosts")
        self.button_update_host.setEnabled(False)
        self.button_update_host.clicked.connect(self.on_update_host_click)
        results_info_layout.addWidget(self.button_update_host)

        button_open_host = QPushButton("打开Hosts")
        button_open_host.clicked.connect(self.on_open_host_click)
        results_info_layout.addWidget(button_open_host)

        results_layout.addLayout(results_info_layout)

        results_section.setLayout(results_layout)
        return results_section

    def create_status_section(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")

        version_label = QLabel(f'版本号: {__version__}', self)
        self.status_bar.addPermanentWidget(version_label)

    def get_domains(self):
        return [domain.strip() for domain in self.text_domains.toPlainText().strip().splitlines() if domain.strip()]

    def get_valid_domains(self):
        domains = self.get_domains()
        return [domain for domain in domains if utils.is_valid_domain(domain)]

    def on_text_domains_changed(self):
        self.clear_highlight(self.text_domains)
        domains = self.get_domains()
        valid_domains = [domain for domain in domains if utils.is_valid_domain(domain)]
        invalid_domains_count = len(domains) - len(valid_domains)
        label_text = f'{len(domains)} 个域名'
        if invalid_domains_count:
            label_text += f'（{invalid_domains_count} 个域名无效）'
            self.highlight_invalid_domains(domains)
        self.label_domains.setText(label_text)
        if valid_domains and len(valid_domains) <= self.config.max_domain_count:
            self.button_query.setEnabled(True)
        else:
            self.button_query.setEnabled(False)

    def on_text_ips_changed(self):
        self.clear_highlight(self.text_ips)
        line_ips = self.text_ips.toPlainText().strip().splitlines()
        ip_domains = [ip.strip() for ip in line_ips if ip.strip() and not ip.startswith('#')]
        valid_ip_domains = [ip_domain for ip_domain in ip_domains if utils.is_valid_ip_domain(ip_domain)]
        invalid_ip_domains_count = len(ip_domains) - len(valid_ip_domains)
        label_text = f'{len(ip_domains)} 个IP-域名'
        if invalid_ip_domains_count:
            label_text += f'（{invalid_ip_domains_count} 个无效）'
            self.highlight_invalid_ip_domains(ip_domains)
        self.label_ip_domains.setText(label_text)
        if valid_ip_domains:
            self.button_update_host.setEnabled(True)
        else:
            self.button_update_host.setEnabled(False)

    def on_reset_click(self):
        self.text_domains.clear()
        self.text_domains.insertPlainText(self.config.default_input_domains)

    def on_query_click(self):
        if self.is_querying:
            self.update_status_bar(self.status_bar.currentMessage() + '请稍候……')
            return

        self.is_querying = True
        self.start_time = datetime.datetime.now()
        valid_domains = self.get_valid_domains()
        if valid_domains:
            self.update_status_bar('查询中，请稍候……')
            self.query_qthread = QueryQThread(valid_domains)
            self.query_qthread.queryCompleted.connect(self.on_query_callback)
            self.query_qthread.queryException.connect(self.on_query_exception_callback)
            self.query_qthread.start()

    @pyqtSlot(dict)
    def on_query_callback(self, domain_ips):
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
        used_time = current_time - self.start_time
        self.update_status_bar(f"查询用时 {used_time.total_seconds()} 秒")
    
    @pyqtSlot(str)
    def on_query_exception_callback(self, error_message):
        self.is_querying = False
        self.update_status_bar(error_message)
        QMessageBox.critical(self, "错误", error_message, QMessageBox.Ok)

    def text_ips_insert(self, context):
        self.text_ips.clear()
        self.text_ips.insertPlainText(context)
        self.set_tab_width()

    def set_tab_width(self):
        tab_width = 150  # 设置Tab键的宽度为150像素

        # 创建一个QTextOption对象
        option = QTextOption()
        option.setTabStop(tab_width)

        # 设置文本编辑器的默认文本选项
        self.text_ips.document().setDefaultTextOption(option)


    def on_update_host_click(self):
        answer_yes = QMessageBox.question(self, "确认", "你确定要执行此操作吗？", QMessageBox.Yes | QMessageBox.No)
        if answer_yes == QMessageBox.Yes:
            host_context = self.text_ips.toPlainText().strip()

            self.update_status_bar('正在更新Hosts……')
            utils.update_hosts_file(host_context)
            self.update_status_bar('更新完成')
            QMessageBox.information(self, "提示", "更新完成")

    def on_open_host_click(self):
        utils.open_hosts_file()

    def update_status_bar(self, context):
        self.status_bar.showMessage(context)

    def clear_highlight(self, text_widget):
        # 记录光标的当前位置
        current_position = text_widget.textCursor().position()
        # 创建一个QTextCursor并选择整个文本
        cursor = text_widget.textCursor()
        cursor.select(QTextCursor.Document)
        
        format = QTextCharFormat()
        format.setBackground(Qt.white)
        text_widget.blockSignals(True)
        cursor.setCharFormat(format)
        text_widget.blockSignals(False)
        cursor.clearSelection()
        cursor.setPosition(current_position)
        text_widget.setTextCursor(cursor)

    def highlight_text(self, text_widget, line_number):
        # 记录光标的当前位置
        current_position = text_widget.textCursor().position()

        block = text_widget.document().findBlockByNumber(line_number)
        cursor = text_widget.textCursor()
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 1)
        format = QTextCharFormat()
        format.setBackground(Qt.yellow)
        text_widget.blockSignals(True)
        cursor.setCharFormat(format)
        text_widget.blockSignals(False)

        # 还原光标位置
        cursor.setPosition(current_position)
        text_widget.setTextCursor(cursor)

    def highlight_invalid_domains(self, domains):
        for i, line in enumerate(self.text_domains.toPlainText().splitlines()):
            if not utils.is_valid_domain(line.strip()):
                self.highlight_text(self.text_domains, i)

    def highlight_invalid_ip_domains(self, domains):
        for i, line in enumerate(self.text_ips.toPlainText().splitlines()):
            if not line.startswith('#') and not utils.is_valid_ip_domain(line.strip()):
                self.highlight_text(self.text_ips, i)

if __name__ == '__main__':
    if cli.main(True):
        app = QApplication(sys.argv)
        ex = App()
        ex.show()
        sys.exit(app.exec_())

# 执行这个命令生成exe文件
# pyinstaller -F main_qt5.py -n Hostip --add-data 'icon.ico;.' -i icon.ico -w
