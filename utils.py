import re
import os
import subprocess
import platform

def path(filename):
    application_path = os.path.dirname(os.path.realpath(__file__))    
    return os.path.join(application_path, filename)

def is_valid_ip(ip):
    # 使用正则表达式匹配 IPv4 地址
    pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))

def is_valid_domain(domain):
    # 使用正则表达式匹配域名格式
    pattern = r"^([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))

def is_valid_ip_domain(ip_domain):
    # 使用正则表达式匹配合法的IP地址-域名
    ipdomain = ip_domain.split()
    return len(ipdomain) == 2 and is_valid_ip(ipdomain[0]) and is_valid_domain(ipdomain[1])

def get_hosts_file_path():
    system = platform.system()
    if system == "Windows":
        # Windows系统下的hosts文件路径
        return os.path.join(os.path.expandvars("%SystemRoot%"), 'system32', 'drivers', 'etc', 'hosts')
    elif system == "Darwin" or system == "Linux":
        # macOS和Linux系统下的hosts文件路径
        return '/etc/hosts'
    else:
        # 不支持的操作系统
        return None

def update_hosts_file(host_context):
    hosts_path = get_hosts_file_path()
    if not hosts_path:
        return

    with open(hosts_path, 'r') as f:
        old_content = f.read()

    pattern = r'# Hostip Host Start([\s\S]*?)# Hostip Host End'
    new_content = re.sub(pattern, host_context, old_content, flags=re.DOTALL)

    if new_content == old_content:
        new_content = old_content + '\r\n\r\n' + host_context

    with open(hosts_path, 'w') as f:
        f.write(new_content)
    
    # 刷新 DNS 缓存
    refresh_dns_cache()

def open_hosts_file():
    hosts_path = get_hosts_file_path()
    if not hosts_path:
        return
    subprocess.Popen(['notepad', hosts_path], shell=True)

def refresh_dns_cache():
    # 刷新 DNS 缓存
    system = platform.system()

    if system == "Windows":
        # 刷新DNS缓存命令（Windows）
        subprocess.run(["ipconfig", "/flushdns"], text=True, check=True)
    elif system == "Darwin" or system == "Linux":
        # 刷新DNS缓存命令（macOS和Linux）
        subprocess.run(["sudo", "systemd-resolve", "--flush-caches"], text=True, check=True)
        # 如果你的系统不使用systemd-resolve，则可以使用以下命令（具体命令可能因Linux发行版而异）：
        # subprocess.run(["sudo", "/etc/init.d/nscd", "restart"], text=True, check=True)
        # 或
        # subprocess.run(["sudo", "service", "dnsmasq", "restart"], text=True, check=True)
    else:
        print("Unsupported operating system")