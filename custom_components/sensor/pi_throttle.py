#!/usr/bin/python3
import logging

import subprocess
import json
import sys
from datetime import timedelta
import json

import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

#REQUIREMENTS = ['sure_petcare']


_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=300)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([pi_throttling()])


class pi_throttling(Entity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        _LOGGER.debug('Initializing...')
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Raspberry PI throttle check'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ''

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.debug('Returning current state...')
        throttling = get_throttled()
        self._state = json.dumps(throttling)
        self._attributes = throttling

    @property
    def state_attributes(self):
        """Return the attributes of the entity.

           Provide the parsed JSON data (if any).
        """

        return self._attributes
    
def convert_vcgencmd(hexval):
    throtteling={}
    binstr = bin(int(hexval,16))[2:].zfill(18)[::-1]
    throtteling['under-voltage']=bool(int(binstr[0]))
    throtteling['arm_frequency_capped']=bool(int(binstr[1]))
    throtteling['currently_throttled']=bool(int(binstr[2]))
    throtteling['under-voltage_has_occured']=bool(int(binstr[16]))
    throtteling['arm_frequency_capped_has_occured']=bool(int(binstr[17]))
    throtteling['thotteling_has_occured']=bool(int(binstr[18]))
    if int("0x00001",16) > 0:
        throtteling['event'] = True
    else:
        throtteling['event'] = False
    return throtteling

def get_throttled():
    throtteling = subprocess.check_output(["/opt/vc/bin/vcgencmd", "get_throttled"]).decode('utf-8').strip()
    throtteling = throtteling.split('=')[1]
    throtteling = convert_vcgencmd(throtteling)
    return throtteling

