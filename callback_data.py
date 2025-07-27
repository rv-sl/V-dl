import hashlib

# You can replace this with a persistent database or file
callback_data_store = {}

def store_callback_data(data: str) -> str:
    key = hashlib.md5(data.encode()).hexdigest()[:10]
    callback_data_store[key] = data
    return key

def get_callback_data(key: str) -> str:
    return callback_data_store.get(key)
