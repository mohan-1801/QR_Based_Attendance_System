import json
import base64
import hashlib
import time
import secrets
from django.conf import settings
from django.utils import timezone

def generate_secure_token():
    return secrets.token_urlsafe(32)

def encrypt_qr_payload(data_dict):
    """
    Serializes payload dict and returns an obfuscated base64 encoded token with salt/hash verification.
    """
    json_str = json.dumps(data_dict, sort_keys=True)
    raw_bytes = json_str.encode('utf-8')
    encoded = base64.urlsafe_b64encode(raw_bytes).decode('utf-8')
    sig = hashlib.sha256((encoded + settings.SECRET_KEY).encode('utf-8')).hexdigest()[:16]
    return f"{encoded}.{sig}"

def decrypt_qr_payload(token_string):
    """
    Validates token signature and decodes JSON payload. Returns dict or None.
    """
    try:
        parts = token_string.split('.')
        if len(parts) != 2:
            return None
        encoded, sig = parts[0], parts[1]
        expected_sig = hashlib.sha256((encoded + settings.SECRET_KEY).encode('utf-8')).hexdigest()[:16]
        if not secrets.compare_digest(sig, expected_sig):
            return None
        decoded_bytes = base64.urlsafe_b64decode(encoded.encode('utf-8'))
        return json.loads(decoded_bytes.decode('utf-8'))
    except Exception:
        return None
