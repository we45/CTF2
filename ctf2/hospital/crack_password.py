
'''
MD5 Password Cracking Script
'''
import requests
import json
import subprocess
import os
from colorama import init, Fore, Back, Style
import sys
import hashlib
init(autoreset=True)


def crack_api_passwords():
    john = '/labs/john/run/john'
    if os.path.exists(john):
        val = raw_input('Enter a String to convert it into hash :')
        h = hashlib.md5()
        h.update(val)
        md5_det = h.hexdigest()
        hashfile = open('hashes.txt', 'w').close()
        hashfile = open('hashes.txt', 'a')
        
        print(Fore.GREEN + '[+] Loading Hash into file for cracking....')
        hashfile.write(md5_det+'\n')
        
        hashfile.close()
        fpath = os.path.abspath('hashes.txt')
        print fpath
        print(Fore.BLUE + '[+] Successfully written to file %s. Cracking with John' % fpath)
        subprocess.call([john,'--format=raw-md5', fpath])
        subprocess.call([john, '--format=raw-md5', fpath, '--show'])
    else:
        john = raw_input('Please enter correct path for John : ')


if __name__ == '__main__':
    crack_api_passwords()
    
