import logging
import json
import os
from os.path import basename
from urllib.parse import urlparse
import voluptuous as vol
from whatsapp_api_client_python import API
import homeassistant.helpers.config_validation as cv
from homeassistant.components.notify import (
    ATTR_TARGET, ATTR_TITLE, ATTR_DATA, PLATFORM_SCHEMA, BaseNotificationService)

ATTR_INSTANCE = "instance_id"
ATTR_TOKEN = "token"


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    # vol.Required(ATTR_TARGET): cv.string,
    vol.Required(ATTR_INSTANCE): cv.string,
    vol.Required(ATTR_TOKEN): cv.string,
    vol.Optional(ATTR_TITLE): cv.string,
})

def get_service(hass, config, discovery_info=None):
    """Get the custom notifier service."""
    title = config.get(ATTR_TITLE)
    token = config.get(ATTR_TOKEN)
    instance_id = config.get(ATTR_INSTANCE)
    return GreenAPINotificationService(title, token, instance_id)

class GreenAPINotificationService(BaseNotificationService):
    
    def __init__(self, title, token,instance_id):
        """Initialize the service."""
        self._title = title
        self._token = token
        self._instance_id = instance_id
        self._greenAPI = API.GreenAPI(self._instance_id, self._token)

    def send_message(self, message="", **kwargs):
        
        """Send a message to the target."""
        
        try:
            data = kwargs.get(ATTR_DATA)
            target = kwargs.get(ATTR_TARGET)[0]
            _LOGGER.info(f"Sending message to {target}")
            if data is not None:
                file_path = data["file"]
                if os.path.exists(file_path):
                    upload_file_response = self._greenAPI.sending.uploadFile(file_path)
                    if upload_file_response.code == 200:
                        url_file = upload_file_response.data["urlFile"]
                        url = urlparse(url_file)
                        file_name = basename(url.path)
                        send_file_by_url_response = self._greenAPI.sending.sendFileByUrl(target, url_file, file_name, caption=message)
            else:
                self._greenAPI.sending.sendMessage(target, message)
        except Exception as e:
            _LOGGER.error("Sending message to %s: has failed with the following error %s", kwargs.get(ATTR_TARGET)[0] ,str(e))