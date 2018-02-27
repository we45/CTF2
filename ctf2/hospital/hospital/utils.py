# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from base64 import b64decode,b64encode
from os import urandom

class TestEncyption:
	def __init__(self):
		self.BLOCK_SIZE = 32
		self.PADDING = '~'
		self.key = urandom(32)
		self.iv = urandom(16)

	def pad(self,s):
		return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING

	def EncodeAES(self,c,s):
		return b64encode(c.encrypt(self.pad(s)))

	def DecodeAES(self,c,e):
		return c.decrypt(b64decode(e)).rstrip(self.PADDING)

	def modes(self,message,mode='ECB'):
		print '\n'*2
		print 'Entered string is ',message		
		print '-'*120
		print '%s mode'%mode
		print '-'*120		
		mode_dict = {
			'CBC':AES.MODE_CBC,
			'ECB':AES.MODE_ECB,
			'CFB':AES.MODE_CFB,
		}
		enc_mode = mode_dict.get(mode)
		if enc_mode:
			enc_obj = AES.new(self.key, enc_mode, self.iv)
			dec_obj = AES.new(self.key, enc_mode, self.iv)
			ciphertext1 = self.EncodeAES(enc_obj, message)
			# print 'Encrypted string ',ciphertext1
			decrypted1 = self.DecodeAES(dec_obj, ciphertext1)
			# print 'Decrypted string ',decrypted1
			ciphertext2 = self.EncodeAES(enc_obj, decrypted1)
			# print 'Encrypted string ',ciphertext
			decrypted2 = self.DecodeAES(dec_obj, ciphertext2)
			# print 'Decrypted string ',decrypted2
			return (ciphertext1,decrypted1,ciphertext2,decrypted2)
		else:
			return ()


	


	
