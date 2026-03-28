# __init__.py

from .jellyfin import Jellyfin
from .navidrome import Navidrome, NavidromeIntegrated
from .local import Local
from .base import Base
from . import models, secret
from ..constants import DATA_DIR
import os, requests
from gi.repository import Gio

integration = None

def get_all_subclasses(cls):
    subclasses = set()
    for s in cls.__subclasses__():
        subclasses.add(s)
        subclasses.update(get_all_subclasses(s))
    return subclasses

def get_available_integrations() -> dict:
    integrations = {}
    for cls in get_all_subclasses(Base):
        integrations[cls.__gtype_name__] = cls
    return integrations

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
    settings = Gio.Settings(schema_id="com.jeffser.Nocturne")
    settings.set_string('selected-instance-type', integration.__gtype_name__)
    if integration.find_property('url'):
        settings.set_string('integration-ip', integration.get_property('url'))
    if integration.find_property('user'):
        settings.set_string('integration-user', integration.get_property('user'))
    if integration.find_property('library_dir'):
        settings.set_string("integration-library-dir", integration.get_property('library_dir'))

