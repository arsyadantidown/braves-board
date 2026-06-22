from datetime import datetime, timezone
from jose import jwt
from app.lib.jwt_utils import create_access_token, create_refresh_token
from app.settings import settings

def test_create_access_token():
    test_data = {"sub": "user_id_123", "role": "admin"}
    
    token = create_access_token(data=test_data)
    
    assert isinstance(token, str)
    
    decoded_payload = jwt.decode(
        token, 
        settings.JWT_SECRET, 
        algorithms=[settings.ALGORITHM]
    )
    
    assert decoded_payload["sub"] == "user_id_123"
    assert decoded_payload["role"] == "admin"
    assert decoded_payload["type"] == "access"
    
    assert "exp" in decoded_payload
    assert decoded_payload["exp"] > datetime.now(timezone.utc).timestamp()

def test_create_refresh_token():
    test_data = {"sub": "user_id_123"}
    
    token = create_refresh_token(data=test_data)
    
    assert isinstance(token, str)
    
    decoded_payload = jwt.decode(
        token, 
        settings.JWT_SECRET, 
        algorithms=[settings.ALGORITHM]
    )
    
    assert decoded_payload["sub"] == "user_id_123"
    assert decoded_payload["type"] == "refresh"
    assert "exp" in decoded_payload
