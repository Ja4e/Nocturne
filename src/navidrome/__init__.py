# __init__.py

from .navidrome import Navidrome
from .local import Local
from . import models, secret

integration = None

def ping_without_login(url:str) -> bool:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('subsonic-response') is not None
    return False

def get_current_integration():
    global integration
    return integration

def set_current_integration(new_integration):
    global integration
    integration = new_integration
