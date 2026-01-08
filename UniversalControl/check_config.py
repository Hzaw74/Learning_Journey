
try:
    with open('/etc/bluetooth/main.conf', 'r') as f:
        print("--- CONTENT START ---")
        print(f.read())
        print("--- CONTENT END ---")
except PermissionError:
    print("Permission denied! Run with sudo.")
except FileNotFoundError:
    print("File not found!")
