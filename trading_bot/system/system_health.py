import psutil
import time

# Ensure required libraries are installed
# pip install psutil

# Thresholds for system health
CPU_THRESHOLD = 85  # Max CPU usage in percentage
RAM_THRESHOLD = 85  # Max RAM usage in percentage
NETWORK_THRESHOLD = 50  # Min network speed in KB/s (example)

def get_cpu_usage():
    """Returns the current system CPU usage as a percentage."""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Returns the current system memory usage as a percentage."""
    memory_info = psutil.virtual_memory()
    return memory_info.percent

def get_disk_usage():
    """Returns the current system disk usage as a percentage."""
    disk_info = psutil.disk_usage('/')
    return disk_info.percent

def get_system_health():
    """Returns a dictionary with the current system health metrics."""
    return {
        'cpu_usage': get_cpu_usage(),
        'memory_usage': get_memory_usage(),
        'disk_usage': get_disk_usage()
    }

def monitor_system_health():
    """Checks system performance and ensures trading bot operates within safe limits."""
    
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    net_speed = psutil.net_io_counters().bytes_sent / 1024  # Convert to KB/s

    print(f"📊 System Health Check: CPU: {cpu_usage}%, RAM: {ram_usage}%, Network: {net_speed:.2f} KB/s")

    if cpu_usage > CPU_THRESHOLD:
        print("❌ Warning: High CPU usage detected!")
        return False
    if ram_usage > RAM_THRESHOLD:
        print("❌ Warning: High RAM usage detected!")
        return False
    if net_speed < NETWORK_THRESHOLD:
        print("❌ Warning: Low network speed detected!")
        return False

    return True

if __name__ == "__main__":
    while True:
        status = monitor_system_health()
        if not status:
            print("⚠️ System under high load! Consider stopping the bot.")
        time.sleep(10)  # Check every 10 seconds
