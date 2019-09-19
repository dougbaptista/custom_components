import requests
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['beautifulsoup4==4.6.3']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "GreenCard"
CONF_CPF = "cpf"
CONF_SENHA = "senha"
CONF_URL_LOGIN = "url_login"
CONF_URL_EXTRACT = "url_extract"

DEFAULT_URL_LOGIN = 'https://www.grupogreencard.com.br/sysweb/site/loga_usuario'
DEFAULT_URL_EXTRACT = 'https://www.grupogreencard.com.br/sysweb/site/areaUsuario'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CPF): cv.string,
    vol.Required(CONF_SENHA): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_URL_LOGIN, default=DEFAULT_URL_LOGIN): cv.string,
    vol.Optional(CONF_URL_EXTRACT, default=DEFAULT_URL_EXTRACT): cv.string,
})
 
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up GreenCard sensor."""
    sensor_cpf = config.get(CONF_CPF)
    sensor_name = config.get(CONF_NAME)
    sensor_senha = config.get(CONF_SENHA)

    sensor_url_login = config.get(CONF_URL_LOGIN)
    sensor_url_extrato = config.get(CONF_URL_EXTRACT)

    add_devices([GreenCard(sensor_name, sensor_cpf, sensor_senha, sensor_url_login, sensor_url_extrato)])

class GreenCard(Entity):
    """Implementation of the green card sensor."""

    def __init__(self, sensor_name, sensor_cpf, sensor_senha, sensor_url_login, sensor_url_extrato):
        """Initialize the sensor."""
        self._senha = sensor_senha
        self._cpf = sensor_cpf
        self._name = sensor_name
        self._url_login = sensor_url_login
        self._url_extrato = sensor_url_extrato
        self._state = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return 'mdi:cash-usd-outline'

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        from bs4 import BeautifulSoup
        
        session = requests.Session()
        form = session.get(self._url_login)

        soup = BeautifulSoup(form.text, 'html.parser')

        imgCaptcha = soup.select('div.eL-captcha > p > strong')[0].text
        imgCaptcha = soup.find('img', alt=imgCaptcha)['data-value']

        payload = {
            'cpf': self._cpf,
            'senha': self._senha,
            'captcha-value': imgCaptcha
        }

        login = session.post(self._url_login, data=payload)

        soup = BeautifulSoup(login.text, 'html.parser')

        success = len(soup.body.findAll(text=self._cpf)) > 0

        if not success:
            self._state = 'Erro ao efetuar login: ', soup.find('div', id='erro')
        else:

            try:

                cod_prod = soup.find('input', {'name': 'COD_PROD'}).get('value')
                num_card = soup.find('input', {'name': 'NUM_CARTAO'}).get('value')
    
                payload = {
                    'COD_PROD': cod_prod,
                    'NUM_CARTAO': num_card
                }
    
                extract = session.post(self._url_extrato, data=payload)
    
                soup = BeautifulSoup(extract.text, 'html.parser')
                saldoReais = soup.select('div.saldo')[0].text
                saldo = saldoReais.replace("R$ ", "")
                
            except IndexError:
                _LOGGER.error("Unable to extract data from HTML")
                return
        
        self._state = saldo


