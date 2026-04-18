import requests
from datetime import datetime
import os
import re
import threading
import csv
from rich.console import Console

class Alive:
    # 初始化类变量
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    urls = []
    thread_count = 10
    scan_lock = threading.Lock()
    result_file = None

    # 清理目标列表
    def clean(self):
        self.urls = []

    # 检查目标文件
    def check_file(self):
        if not os.path.exists("targets.txt"):
            with open("targets.txt", "w", encoding="utf-8") as f:
                f.write("baidu.com\n")
            print("\033[31m[!] 目标文件 targets.txt 不存在！已创建。\033[0m")

    # 检查目标文件是否为空
    def check_target(self):
        try:
            with open("targets.txt", "r", encoding="utf-8") as f:
                if f.read().strip() == "":
                    print("\033[31m[!] 目标文件 targets.txt 为空！\033[0m")
                    print("\033[31m[!] 请注意添加查询目标到 targets.txt 文件中！\033[0m")
        except Exception as e:
            print(f"\033[31m[!] 检查目标文件失败: {e}\033[0m")

    # 读取目标文件
    def read_file(self):
        try:
            with open("targets.txt", "r", encoding="utf-8") as f:
                self.urls = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"\033[31m[!] 读取文件 targets.txt 失败: {e}\033[0m")

    # 规范化URL
    def normalize_url(self, url):
        if not re.match(r"^https?://", url):
            url = "https://" + url
        return url
    
    # 手动输入URL
    def manual_input(self):
        urls = []
        print("请输入要探测的URL，支持多行输入，空行结束：")
        try:
            while True:
                url = input().strip()
                if url == "":
                    break
                urls.append(url)
            if not urls:
                print("\033[31m[!] 未输入任何URL！\033[0m")
                return False
            self.urls = urls
            return True
        except:
            print("\033[31m[!] 输入错误！\033[0m")
            return False
        
    # 设置线程数
    def set_thread_count(self):
        try:
            choice = input("请输入线程数：").strip()
            if not choice:
                print(f"\033[32m[*] 线程数保持为：{self.thread_count}\033[0m")
            if choice:
                self.thread_count = int(choice)
                print(f"\033[32m[*] 线程数已设置为：{self.thread_count}\033[0m")
        except:
            print("\033[31m[!] 输入错误！\033[0m")

    # 探测URL
    def scan_url(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=2.5)
            code = response.status_code
            length = len(response.text)
            
            title = "无标题"
            raw_content = response.content
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    text = raw_content.decode(encoding)
                    title_match = re.search(r'<title>(.*?)</title>', text)
                    if title_match:
                        title = title_match.group(1).strip()
                        break
                except:
                    continue
            
            with self.scan_lock:
                if code != 404:
                    if title == "无标题":
                        print(f"\033[33m[*] 状态码[\033[32m{code}\033[33m] -> 标题[\033[31m{title}\033[33m] -> 响应长度[\033[32m{length}\033[33m] -> {url}\033[0m")
                    else:
                        print(f"\033[33m[*] 状态码[\033[32m{code}\033[33m] -> 标题[\033[32m{title}\033[33m] -> 响应长度[\033[32m{length}\033[33m] -> {url}\033[0m")
                    self.result_file.write(f"{url}, {code}, {title}, {length}\n")
                    self.result_file.flush()
                else:
                    print(f"\033[35m[*] 状态码[{code}] -> 标题[{title}] -> 响应长度[{length}] -> {url}\033[0m")
        except:
            with self.scan_lock:
                print(f"\033[31m[!] 目标死亡或请求失败 -> {url}\033[0m")
        
    # 开始探测
    def scan(self):
        print("\033[33m[+] 开始探测...\033[0m")
        
        if not self.urls:
            print("\033[31m[!] 没有有效的URL可探测！\033[0m")
            return
        
        if not os.path.exists("result"):
            os.makedirs("result", exist_ok=True)
        
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_path = os.path.join("result", f"{current_time}.csv")
        
        try:
            self.result_file = open(csv_path, "w", encoding="utf-8", newline="")
            writer = csv.writer(self.result_file)
            writer.writerow(["URL", "状态码", "标题", "响应长度"])
            
            normalized_urls = [self.normalize_url(url) for url in self.urls]
            normalized_urls = list(set(normalized_urls))
            
            thread_urls = [[] for _ in range(self.thread_count)]
            for i, url in enumerate(normalized_urls):
                thread_urls[i % self.thread_count].append(url)
            
            threads = []
            for urls in thread_urls:
                for url in urls:
                    t = threading.Thread(target=self.scan_url, args=(url,))
                    t.start()
                    threads.append(t)
            
            for t in threads:
                t.join()
            
            self.result_file.close()
            
            if os.path.getsize(csv_path) <= 35:
                print("\033[31m[!] 探测结束！没有存活目标！\033[0m")
                os.remove(csv_path)
            else:
                print(f"\033[33m[+] 探测结束！存活目标已保存到 {csv_path}\033[0m")
        except Exception as e:
            print(f"\033[31m[!] 保存结果失败: {e}\033[0m")

console = Console()
text = [
"\n",
"██████╗ ██╗   ██╗             █████╗ ██╗     ██╗██╗   ██╗███████╗██╗  ██╗",
"██╔══██╗██║   ██║            ██╔══██╗██║     ██║██║   ██║██╔════╝╚██╗██╔╝",
"██████╔╝██║   ██║   █████╗   ███████║██║     ██║██║   ██║█████╗   ╚███╔╝",
"██╔══██╗██║   ██║   ╚════╝   ██╔══██║██║     ██║╚██╗ ██╔╝██╔══╝   ██╔██╗",
"██████╔╝╚██████╔╝            ██║  ██║███████╗██║ ╚████╔╝ ███████╗██╔╝ ██╗",
"╚═════╝  ╚═════╝             ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝",
"————————————————————— Bu-AliveX v1.0.0 - 存活检测工具 —————————————————————",
"[*] 项目地址:[blue]https://github.com/Bu7terf1y/Bu-AliveX[/blue]",
"[*] By.Bu7terf1y",
"[*] 说明:批量检测域名是否存活的目标文件为 targets.txt"
]

start = (255, 182, 193)
end = (128, 0, 128)

lines = len(text)

for i, line in enumerate(text):
    r = int(start[0] + (end[0] - start[0]) * i / (lines - 1))
    g = int(start[1] + (end[1] - start[1]) * i / (lines - 1))
    b = int(start[2] + (end[2] - start[2]) * i / (lines - 1))
    console.print(line, style=f"rgb({r},{g},{b})", highlight=False)

alive = Alive()
alive.check_file()
alive.check_target()

while True:
    print("\n==============================================================")
    choice = input(f"请输入1.手动输入 2.读取文件 3.设置线程（当前：{alive.thread_count}） 4.退出：").strip()
    if choice == "1":
        alive.clean()
        if alive.manual_input():
            alive.scan()
    elif choice == "2":
        alive.clean()
        alive.read_file()
        alive.scan()
    elif choice == "3":
        alive.set_thread_count()
    elif choice == "4":
        print("\033[33m[+] 程序退出！\033[0m")
        break
    else:
        print("\033[31m[!] 输入错误！请输入1、2、3或4。\033[0m")