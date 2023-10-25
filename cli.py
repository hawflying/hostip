import argparse
import utils
import request_util
import datetime
from config import Config

def create_arg_parser():
    parser = argparse.ArgumentParser(description="Hostip - Query and Update Hosts file.")
    parser.add_argument("--query", action="store_true", help="Query IP addresses for domains.")
    parser.add_argument("--auto-update", action="store_true", help="Automatically update Hosts without asking.")
    parser.add_argument("--domains", nargs="+", default=None, help="Specify domains for query.")
    return parser

def main(isparser = False):
    parser = create_arg_parser()
    args = parser.parse_args()

    if isparser and not args.query and not args.auto_update:
        return True

    domains = args.domains

    if not domains and not args.auto_update:
        input_text = input("Press enter to skip and use default domain name or enter the domain name of the IP address to be queried:\r\n")
        if input_text:
            domains = input_text.replace(' ', ',').split(',')

    if not domains:
        # 如果未指定要查询的域名，从配置文件中读取默认的域名列表
        domains = Config().default_input_domains.splitlines()

    if not domains:
        print("No domains specified. Exiting.")
        return

    # 校验输入的域名是否合法
    invalid_domains = [domain for domain in domains if not utils.is_valid_domain(domain)]
    if invalid_domains:
        print(f"Invalid domains found: {', '.join(invalid_domains)}")
        return

    print("Domain name of the IP address to be queried:")
    print("\r\n".join(domains) + "\r\n")
    print("Finding IP addresses...\r\n")

    # 查询IP地址
    domain_ips = request_util.batch_query(domains)
    if not domain_ips:
        print("No IP addresses found. Exiting.")
        return

    host_ips = "\r\n".join([f"{ip_address}\t{domain}" for domain, ip_address in domain_ips.items()])
    print("IP addresses found:")
    print(host_ips + "\r\n")

    current_time = datetime.datetime.now()
    host_context = f"""# Hostip Host Start
# {list(domain_ips.keys())[0]} {len(domain_ips)} domain IP addresses
{host_ips}
# Update time: {current_time}
# Hostip Host End"""
    
    if args.auto_update:
        utils.update_hosts_file(host_context)
        print("Hosts file updated automatically.")
    else:
        answer = input("Do you want to update Hosts with the query results? (yes/no): ")
        if answer.lower() == "yes":
            utils.update_hosts_file(host_context)
            print("Hosts file updated successfully")

if __name__ == '__main__':
    main()