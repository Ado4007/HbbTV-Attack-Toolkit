from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    sid: str
    ip: str
    info: Optional[dict]
    scan: Optional[dict]

class ClientManager():
    def __init__(self, logger):
        self.clients = []
        self.logger = logger
    
    def add_client(self, sid, ip, info=None):
        self.clients.append(Client(sid, ip, info, None))
        self.logger.info(f"Client {sid} from ip: {ip} connected! {info}")

    def remove_client(self, sid):
        self.clients = [c for c in self.clients if c.sid != sid]
        self.logger.info(f"Client {sid} disconnected!")
    
    def get_client(self, index):
        return self.clients[index]
    
    def get_client_by_sid(self, sid):
        return next((client for client in self.clients if client.sid == sid), None)
    
    def get_all_clients(self):
        return self.clients