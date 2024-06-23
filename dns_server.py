import pickle
import socket
from datetime import datetime, timedelta
from dnslib import DNSRecord, RCODE

CACHE_FILE = 'dns_cache.pickle'
CACHE_TTL = 10


class CacheManager:
    def __init__(self):
        self.entries = {}

    def store_entry(self, query_key, dns_record):
        self.entries[query_key] = (dns_record, datetime.now())

    def fetch_entry(self, query_key):
        if query_key in self.entries:
            dns_record, timestamp = self.entries[query_key]
            if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL):
                return dns_record
            else:
                print(f' запись {query_key} удалена')
                del self.entries[query_key]
        return None

    def save_entries(self):
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(self.entries, f)

    def load_entries(self):
        try:
            with open(CACHE_FILE, "rb") as f:
                self.entries = pickle.load(f)
        except FileNotFoundError:
            pass


class DnsService:
    def __init__(self):
        self.cache_manager = CacheManager()
        self.cache_manager.load_entries()

    def handle_query(self, request_data):
        try:
            dns_query = DNSRecord.parse(request_data)
            query_key = (dns_query.q.qname, dns_query.q.qtype)
            cached_record = self.cache_manager.fetch_entry(query_key)

            if cached_record:
                print(f"Запись найдена в кэше")
                return cached_record.pack()

            response = dns_query.send('8.8.8.8')
            response_record = DNSRecord.parse(response)
            if response_record.header.rcode == RCODE.NOERROR:
                self.cache_manager.store_entry(query_key, response_record)
                self.cache_manager.save_entries()
                print(f"Добавлена запись в кэш")
            return response
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', 53))

        print("DNS Сервер запущен.")

        while True:
            try:
                request_data, client_address = sock.recvfrom(1024)
                print(f'Получен запрос от: {client_address}')
                response_data = self.handle_query(request_data)
                if response_data:
                    sock.sendto(response_data, client_address)

            except KeyboardInterrupt:
                print("Завершение работы сервера.")
                sock.close()


dns_service = DnsService()
dns_service.start_server()