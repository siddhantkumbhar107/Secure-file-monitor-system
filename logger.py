from datetime import datetime

def log_event(data):
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} | {data}\n")