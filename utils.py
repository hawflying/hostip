import re
import os
import subprocess

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

def update_hosts_file(host_context):
    hosts_path = os.path.join(os.path.expandvars("%SystemRoot%"), 'system32', 'drivers', 'etc', 'hosts')
    with open(hosts_path, 'r') as f:
        old_content = f.read()

    pattern = r'# Hostip Host Start([\s\S]*?)# Hostip Host End'
    new_content = re.sub(pattern, host_context, old_content, flags=re.DOTALL)

    if new_content == old_content:
        new_content = old_content + '\r\n\r\n' + host_context

    with open(hosts_path, 'w') as f:
        f.write(new_content)

def open_hosts_file():
    subprocess.Popen(['notepad', os.path.join(os.path.expandvars("%SystemRoot%"), 'system32', 'drivers', 'etc', 'hosts')], shell=True)