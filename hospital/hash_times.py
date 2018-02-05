import timeit
import bcrypt
import hashlib
from pbkdf2 import crypt
from colorama import Fore

def standard_sha1():
	print(Fore.BLUE + hashlib.sha1("P@55w0rd#1234$").hexdigest())

def bcrypt_hash():
	password = b"P@55w0rd#1234$"
	hashed = bcrypt.hashpw(password, bcrypt.gensalt())
	print(Fore.GREEN + hashed)

def pbkdf2_hash():
	hash_val = crypt("P@55w0rd#1234$",salt="iotdxb2016", iterations=1000)
	print(Fore.CYAN + hash_val)

shatime = timeit.Timer(stmt = "standard_sha1()", setup = "from __main__ import standard_sha1")
bc = timeit.Timer(stmt = "bcrypt_hash()", setup = "from __main__ import bcrypt_hash")
pbk = timeit.Timer(stmt = "pbkdf2_hash()", setup = "from __main__ import pbkdf2_hash")

print(Fore.BLUE + 'Time for 100 Regular SHA-1 Hashes: %s seconds' % str(shatime.timeit(100)))
print '\n'
print(Fore.GREEN + 'Time for 1 BCrypt Hash %s seconds' % str(bc.timeit(1)))
print '\n'
print(Fore.CYAN + 'Time for 1 PBKDF2 Hash %s seconds' % str(pbk.timeit(1)))






