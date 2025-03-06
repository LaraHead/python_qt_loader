import socket

def get_hostname(ip_address):
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return "Не удалось определить имя компьютера"

ip_address = '10.2.71.147'  # Укажите нужный IP-адрес здесь
hostname = get_hostname(ip_address)
print(f"Имя компьютера с IP-адресом {ip_address}: {hostname}")