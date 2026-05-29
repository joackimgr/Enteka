import bcrypt

def hashing(password):
    byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashing = bcrypt.hashpw(byte, salt)
    return hashing.decode('utf-8')

def verify(password, stored_hash):
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True
    else:
        return False
