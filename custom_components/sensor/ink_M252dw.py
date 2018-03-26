#!/usr/bin/python3
import logging

import json
from datetime import timedelta
import urllib3
urllib3.disable_warnings()
import requests
from bs4 import BeautifulSoup
import re

import voluptuous as vol

from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import homeassistant.util as util

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
})

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=3600)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=600)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=120)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    hostip = config.get(CONF_HOST)
    add_devices([ink_M252dw(hostip)])


class ink_M252dw(Entity):
    """Find the ink levels of the M252dw printer"""

    def __init__(self, hostip):
        """Initialize the sensor."""
        _LOGGER.debug('Initializing...')
        self.HOSTIP = hostip
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Ink levels for HP M252dw printer' 

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.debug('Returning current state...')
        ink_levels = get_ink_levels(self.HOSTIP)
        self._state = json.dumps(ink_levels)
        self._attributes = ink_levels

    @property
    def state_attributes(self):
        """Return the attributes of the entity.

           Provide the parsed JSON data (if any).
        """
        return self._attributes
    
def get_ink_levels(HOSTIP):
    try:
        page = requests.get("https://" + HOSTIP + "/hp/device/info_suppliesStatus.html?tab=Home&menu=SupplyStatus", verify=False, timeout=2)
    except requests.exceptions.Timeout:
        return None
    soup = BeautifulSoup(page.content, 'html.parser')
    inkstatus = soup.find_all('td', class_='SupplyName')
    ink_levels={}
    Colours = ['Black','Magenta','Cyan','Yellow']
    if len(inkstatus)==8:
        for i in range(0,8,2):
            for colour in Colours:
                if colour in inkstatus[i].contents[0]:
                    level = re.findall(r'[\d-][\d-]%', inkstatus[i+1].contents[0])[0][0:2]
                    if level == '--':
                        level = 0
                    else:
                        level = int(level)
                    ink_levels[colour]=level
    return ink_levels
