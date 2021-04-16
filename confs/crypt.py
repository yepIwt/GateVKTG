#v.2
from Crypto.Cipher import AES
import hashlib
import os

class LetItCrypt(object):

	def __init__(self, passw: str):
		self.key = hashlib.sha256(passw.encode()).digest()
		self.mode = AES.MODE_EAX

	def pad(self, text: bytes) -> bytes:
		while len(text) % 16 != 0:
			text += b' '
		return text

	def enc_cfg(self, data: str) -> None:
		cipher = AES.new(self.key, self.mode)
		ciphertext, tag = cipher.encrypt_and_digest(data.encode())
		file_out = open("data", "wb")
		[ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
		file_out.close()

	def dec_cfg(self) -> str:
		file_in = open("data", "rb")
		nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
		cipher = AES.new(self.key, self.mode, nonce)
		try:
			data = cipher.decrypt_and_verify(ciphertext, tag)
		except ValueError:
			return ''
		else:
			return data