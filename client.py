import re
import socket
from dnslib import DNSRecord
import random

# Список доменов и типов запросов
domain_names = ['youtube.com']
query_types_list = ['A', 'NS']


def is_ip_address_valid(ip_address):
    ip_check_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    return bool(re.match(ip_check_pattern, ip_address))


def get_ip_from_domain(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return "Не удалось получить IP-адрес"


def get_domain_from_ip(ip_address):
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return "Не удалось получить доменное имя"


def execute_client():
    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_server_address = ('localhost', 53)

    for name in domain_names:
        print('------------------------------------')
        if is_ip_address_valid(name):
            print(f"{name} {get_domain_from_ip(name)}")
        else:
            print(f"{name} {get_ip_from_domain(name)}")

        print('------------------------------------')

        dns_query_data = DNSRecord.question(name, random.choice(query_types_list)).pack()

        udp_client_socket.sendto(dns_query_data, dns_server_address)
        dns_response_data, _ = udp_client_socket.recvfrom(1024)
        dns_response = DNSRecord.parse(dns_response_data)

        print(dns_response)

    udp_client_socket.close()


if __name__ == "__main__":
    execute_client()