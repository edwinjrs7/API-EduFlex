from threading import Lock
from openai import OpenAI
import os

class KeyMaster:
    def __init__(self, api_keys: list):
        self.api_keys = api_keys
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        self.current_index = 0
        self.lock = Lock()
        
    def ObtenerCLiente(self):
        key = self.api_keys[self.current_index]
        return OpenAI(api_key=key, base_url= self.base_url)
    
    def cambioDeKey(self):
        with self.lock:
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            print(f"Cambiando a la siguiente clave API: {self.api_keys[self.current_index]}")