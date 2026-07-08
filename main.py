import subprocess
import threading

def run_bot():
    subprocess.run(["python", "bot.py"])

def run_shop():
    subprocess.run(["python", "shop.py"])

if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot)
    t2 = threading.Thread(target=run_shop)
    
    t1.start()
    t2.start()

