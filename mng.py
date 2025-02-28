import os
from ecies.utils import generate_eth_key
from ecies import encrypt, decrypt
from eth_keys import keys

def clean_privkey(privkey_str: str) -> str:
    if privkey_str.startswith("0x"):
        return privkey_str
    return "0x" + privkey_str

class pwdLst:
    def __init__(self):
        self.pwd = {}
        self.appdata_path = os.path.join(os.getenv('LOCALAPPDATA'), 'PwdMng')
        if not os.path.exists(self.appdata_path):
            os.makedirs(self.appdata_path)
        self.link = os.path.join(self.appdata_path, "mng.pwd")

    def readPwdFileLst(self):
        self.pwd = {}
        try:
            with open(self.link, 'r') as file:
                lines = file.readlines()
                i = 0
                while i < len(lines):
                    if i + 2 < len(lines):
                        domain = lines[i].strip()
                        user = lines[i + 1].strip()
                        pswd = lines[i + 2].strip()
                        self.pwd[domain] = [user, pswd]
                    i += 3
        except FileNotFoundError:
            print("Fichier mng.pwd non trouvé. Création d'un nouveau fichier.")
            self.savePwd()


    def add(self, domain, user, pswd):
        self.pwd[domain] = [user, pswd]

    def getPwd(self):
        return self.pwd
    
    def savePwd(self):
        with open(self.link, 'w') as file:
            for domain in self.pwd:
                file.write(domain + "\n")
                file.write(self.pwd[domain][0] + "\n")
                file.write(self.pwd[domain][1] + "\n")
    
    def remove(self, domain):
        with open(self.link, 'w') as file:
            for d in self.pwd:
                if d != domain:
                    file.write(d + "\n")
                    file.write(self.pwd[d][0] + "\n")
                    file.write(self.pwd[d][1] + "\n")
        for d in self.pwd:
            if d == domain:
                del self.pwd[d]

class initMng:
    def __init__(self, privKey=None):
        self.pwdLst = pwdLst()
        self.pwdDecrypt = []
        if os.path.exists(self.pwdLst.link):
            self.pwdLst.readPwdFileLst()
        else:
            self.pwdLst.savePwd()
        
        if privKey is None:
            eth_key = generate_eth_key()
            self.privKey_hex = eth_key.to_hex()
            self.pubKey_hex = eth_key.public_key.to_hex()
        else:
            privKey_clean = clean_privkey(privKey)
            privkey_bytes = bytes.fromhex(privKey_clean[2:])
            private_key_obj = keys.PrivateKey(privkey_bytes)
            self.privKey_hex = private_key_obj.to_hex()
            self.pubKey_hex = private_key_obj.public_key.to_hex()

    def cryptPwd(self, pwdList):
        for domain in pwdList.keys():
            encrypted_domain = encrypt(self.pubKey_hex, domain.encode()).hex()
            encrypted_user = encrypt(self.pubKey_hex, pwdList[domain][0].encode()).hex()
            encrypted_pwd = encrypt(self.pubKey_hex, pwdList[domain][1].encode()).hex()
            self.pwdLst.add(encrypted_domain, encrypted_user, encrypted_pwd)
        self.pwdLst.savePwd()

    def getPwdDecrypt(self):
        self.pwdDecrypt = []
        for encrypted_domain, (encrypted_user, encrypted_pwd) in self.pwdLst.getPwd().items():
            try:
                domain = decrypt(self.privKey_hex, bytes.fromhex(encrypted_domain)).decode()
                user = decrypt(self.privKey_hex, bytes.fromhex(encrypted_user)).decode()
                pswd = decrypt(self.privKey_hex, bytes.fromhex(encrypted_pwd)).decode()
                self.pwdDecrypt.append((domain, user, pswd))
            except Exception as e:
                self.pwdDecrypt.append(f"Decryption failed: {e}")
        return self.pwdDecrypt
    
    def getPrivKey(self):
        return self.privKey_hex