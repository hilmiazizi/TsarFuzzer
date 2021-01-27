import requests
from colorama import *
import os
import json
import multiprocessing
import random
import tqdm
import time
init(autoreset=True)
os.system('clear')
maiurl = None
def banner():
	print(Style.BRIGHT+Fore.YELLOW+" _____                "+Fore.GREEN+"    ___                       ")
	print(Style.BRIGHT+Fore.YELLOW+"/__   \___  __ _ _ __ "+Fore.GREEN+"   / __\   _ ___________ _ __ ")
	print(Style.BRIGHT+Fore.YELLOW+"  / /\/ __|/ _` | '__|"+Fore.GREEN+"  / _\| | | |_  /_  / _ \ '__|")
	print(Style.BRIGHT+Fore.YELLOW+" / /  \__ \ (_| | |   "+Fore.GREEN+" / /  | |_| |/ / / /  __/ |   ")
	print(Style.BRIGHT+Fore.YELLOW+" \/   |___/\__,_|_|   "+Fore.GREEN+" \/    \__,_/___/___\___|_|   ")
	                                                    


	print(Fore.WHITE+Style.BRIGHT+"""____________________________________________________""")
	print(Fore.GREEN+Style.BRIGHT+"""
\t      Ultimate URL Fuzzer Tools
\t\t     Hilmi Azizi
""")

def CheckMachine(result):
	global domain
	global mainurl
	num_lines = sum(1 for line in open('path.dict'))
	processes = []
	for i in result:
		p = multiprocessing.Process(target=doCheck, args=(i,))
		processes.append(p)
		p.start()
		
	for process in processes:
		process.join()


	print(Fore.YELLOW+Style.BRIGHT+"\n[+] Fuzzing Subdomains.")
	for url in open(domain+"-subdomains.txt"):
		with open('path.dict') as f:
			path = f.read().splitlines()
		mainurl = url.rstrip()
		des = url.split('.')
		des = des[0].split('//')
		des = des[1]
		p = multiprocessing.Pool(multiprocessing.cpu_count())
		r = list(tqdm.tqdm(p.imap(doFuzz, path), total=num_lines, desc=des+".*"))

def doFuzz(path):
	global mainurl
	url = mainurl
	mainurl_format = mainurl.replace('/','')
	mainurl_format = mainurl_format.split(':')
	mainurl_format = mainurl_format[1]

	try:
		result = requests.get(url+path, allow_redirects=True, timeout=5)
		if str(result.status_code) == 404:
			return None
		elif str(result.status_code)[0] == '2' or str(result.status_code)[0] == 3 or str(result.status_code)[0] == 4:
			f = open(mainurl_format+".txt",'a+')
			f.write("["+str(result.status_code)+"]  "+url+path+"\n")
			f.close()
	except:
		return None

def doCheck(url):
	global domain
	try:
		r = requests.get("http://"+url, allow_redirects=True, timeout=2)
		if '>' in r.content and url in r.url:
			sleep = random.uniform(0.0,3)
			time.sleep(sleep)
			print(Style.BRIGHT+Fore.GREEN+"    [+] Live => "+Fore.WHITE+Style.BRIGHT+r.url)
			f = open(domain+"-subdomains.txt",'a+')
			f.write(r.url+'\n')
			f.close()
		
	except:
		return None

def fetchDomain(domain):
	try:
		result = requests.get('https://api.linuxsec.org/api/subdomains?host='+domain)
		result = json.loads(result.content)
		print(Style.BRIGHT+"[+] Subdomains Found: "+Fore.GREEN+str(len(result['results'])))
		return result['results']
	except:
		return None
	

try:
	banner()
	domain = raw_input(Style.BRIGHT+'[?] Domain : ')
	domain = domain.replace('www.','').replace('/','').replace('http:','').replace('https:','')
	
	
	retry = 0
	print(Style.BRIGHT+Fore.YELLOW+"[#] Enumerating Subdomains")
	result = fetchDomain(domain)
	while not result:
		retry+=1
		if retry<=3:
			print(Fore.RED+Style.BRIGHT+"[!] Connection timeout, retry for "+str(retry)+" times.")
			result = fetchDomain(domain)
		else:
			print(Back.RED+Style.BRIGHT+"[!] Maximum retries reached, check your connection or API")
			exit()
	print(Style.BRIGHT+Fore.YELLOW+"[#] Checking Subomains")
	CheckMachine(result)
except KeyboardInterrupt:
	exit()