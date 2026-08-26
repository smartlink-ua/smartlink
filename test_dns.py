import socket
try:
       ip = socket.gethostbyname('nwuijdpamsijypmviwra.supabase.co')
       print(f"✅ DNS працює! Python бачить інтернет. IP: {ip}")
except socket.gaierror as e:
       print(f"❌ Windows/Антивірус БЛОКУЄ запити Python. Помилка: {e}")