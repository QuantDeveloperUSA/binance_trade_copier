from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()
print("New encryption key generated:")
print(f"ENCRYPTION_KEY = {key!r}")
print("\nCopy this key to config.py, replacing the existing ENCRYPTION_KEY value.")
print("Keep this key secret and secure!")
