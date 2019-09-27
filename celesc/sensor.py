import requests
import logging
from datetime import *
from bs4 import BeautifulSoup

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['beautifulsoup4==4.6.3']

_LOGGER = logging.getLogger(__name__)

CONF_UNIDADE_CONSUMIDORA = 'unidade_consumidora'
CONF_CPF = 'cpf'
CONF_SENHA = 'senha'

CONF_PARAM_URL = 'param_url'
CONF_NUMERO_MEDIDOR = 'numero_medidor'
CONF_TP_DOCUMENTO = 'tp_documento'
CONF_AUDTENTICAR_SEM_DOCUMENTO = 'autentitcador_sem_documento'
CONF_TIPO_USUARIO = 'tipo_usuario'

CONF_URL_LOGIN = 'url_login'
CONF_URL_AUTENTICA = 'url_autentica'
CONF_URL_LEITURA = 'url_leitura'

DEFAULT_NAME = "CELESC"
DEFAULT_PARAM_URL = "/agencia/"
DEFAULT_NUMERO_MEDIDOR = "false"
DEFAULT_TP_DOCUMENTO = "CPF"
DEFAULT_AUDTENTICAR_SEM_DOCUMENTO = "false"
DEFAULT_TIPO_USUARIO = "clienteUnCons"

DEFAULT_URL_LOGIN = 'https://agenciaweb.celesc.com.br/AgenciaWeb/autenticar/autenticar.do'
DEFAULT_URL_AUTENTICA = 'https://agenciaweb.celesc.com.br/AgenciaWeb/autenticar/validarSenha.do'
DEFAULT_URL_LEITURA = 'https://agenciaweb.celesc.com.br/AgenciaWeb/consultarDataLeitura/consultarDataLeitura.do'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_UNIDADE_CONSUMIDORA): cv.string,
    vol.Required(CONF_CPF): cv.string,
    vol.Required(CONF_SENHA): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,

    vol.Optional(CONF_PARAM_URL, default=DEFAULT_PARAM_URL): cv.string,
    vol.Optional(CONF_NUMERO_MEDIDOR, default=DEFAULT_NUMERO_MEDIDOR): cv.string,
    vol.Optional(CONF_TP_DOCUMENTO, default=DEFAULT_TP_DOCUMENTO): cv.string,
    vol.Optional(CONF_AUDTENTICAR_SEM_DOCUMENTO, default=DEFAULT_AUDTENTICAR_SEM_DOCUMENTO): cv.string,
    vol.Optional(CONF_TIPO_USUARIO, default=DEFAULT_TIPO_USUARIO): cv.string,

    vol.Optional(CONF_URL_LOGIN, default=DEFAULT_URL_LOGIN): cv.string,
    vol.Optional(CONF_URL_AUTENTICA, default=DEFAULT_URL_AUTENTICA): cv.string,
    vol.Optional(CONF_URL_LEITURA, default=DEFAULT_URL_LEITURA): cv.string,
})
 
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up celesc sensor."""
    sensor_unidade_consumidora = config.get(CONF_UNIDADE_CONSUMIDORA)
    sensor_cpf = config.get(CONF_CPF)
    sensor_name = config.get(CONF_NAME)
    sensor_senha = config.get(CONF_SENHA)

    sensor_param_url = config.get(CONF_PARAM_URL)
    sensor_numero_medidor = config.get(CONF_NUMERO_MEDIDOR)
    sensor_tp_documento = config.get(CONF_TP_DOCUMENTO)
    sensor_autenticar_sem_documento = config.get(CONF_AUDTENTICAR_SEM_DOCUMENTO)
    sensor_tipo_usuario = config.get(CONF_TIPO_USUARIO)

    sensor_url_login = config.get(CONF_URL_LOGIN)
    sensor_url_autentica = config.get(CONF_URL_AUTENTICA)
    sensor_url_leitura = config.get(CONF_URL_LEITURA)

    add_devices([Celesc(sensor_name, sensor_unidade_consumidora, sensor_cpf, sensor_senha, sensor_param_url, sensor_numero_medidor, sensor_tp_documento, sensor_autenticar_sem_documento, sensor_tipo_usuario, sensor_url_login, sensor_url_autentica, sensor_url_leitura)])

class Celesc(Entity):
    """Implementation of the Celesc sensor."""

    def __init__(self, sensor_name, sensor_unidade_consumidora, sensor_cpf, sensor_senha, sensor_param_url, sensor_numero_medidor, sensor_tp_documento, sensor_autenticar_sem_documento, sensor_tipo_usuario, sensor_url_login, sensor_url_autentica, sensor_url_leitura):
        """Initialize the sensor."""
        self._senha = sensor_senha
        self._cpf = sensor_cpf
        self._name = sensor_name
        self._unidade_consumidora = sensor_unidade_consumidora

        self._param_url = sensor_param_url
        self._numero_medidor = sensor_numero_medidor
        self._tp_documento = sensor_tp_documento
        self._autenticar_sem_documento = sensor_autenticar_sem_documento
        self._tipo_usuario = sensor_tipo_usuario

        self._url_login = sensor_url_login
        self._url_autentica = sensor_url_autentica
        self._url_leitura = sensor_url_leitura

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
        return 'mdi:page-next-outline'

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        #dados para login
        payload = {
            'param_url': self._param_url,
            'sqUnidadeConsumidora': self._unidade_consumidora,
            'numeroMedidor': self._numero_medidor,
            'tpDocumento': self._tp_documento,
            'numeroDocumentoCPF': self._cpf,
            'autenticarSemDocumento': self._autenticar_sem_documento,
            'tipoUsuario': self._tipo_usuario
        }

        #cria sessão
        session = requests.Session()

        login = session.post(self._url_login, data=payload)
        soup = BeautifulSoup(login.text, 'html.parser')

        # se encontrar a frase "Digite sua senha" é porque deu certo
        success = len(soup.body.findAll(text='Digite sua senha')) > 0

        #verifica se efetuou o login
        if not success:
            self._state = 'Erro ao efetuar login: ', soup.find('div', class_='textoErroMensagem')
        else:

            #autentica
            payload = {
                'senha': self._senha
            }

            autentica = session.post(self._url_autentica, data=payload)
            soup = BeautifulSoup(autentica.text, 'html.parser')
            
            #pega cpf para comparar (se vpegar o valor do cpf, a página autenticou)
            success = soup.select('div.lineSpacingFixed > span.textoGeral')[1].text
            
            #verifica se autenticou comparando o cpf
            if success == self._cpf:
                leitura = session.post(self._url_leitura)
                soup = BeautifulSoup(leitura.text, 'html.parser')

                #pega as informações da sexta tabela na página HTML
                tbody = soup.select('table')[5]

                #cria a data atual
                data_atual = date.today()

                #define uma variável para fazer o "break" quando encontrar a próxima leitura
                leitura_visualizada = False

                #lê as informações da tabela "tr > td"
                for row in tbody.findAll('tr'):
                    cols = row.find_all('td', class_='textoGeral')
                    
                    #continua só se tiver informação
                    if len(cols) > 0:
                        
                        #pega a data de leitura que fica na terceira coluna
                        captura_data = cols[2].find(text=True).strip()

                        #verifica se a coluna não está vazia
                        if captura_data != '------':
                            
                            #separa a data em várivaveis para converter em date
                            y1, m1, d1 = [int(x) for x in (captura_data.split('-'))]

                            #converte a data em tipo date
                            data_prevista_leitura = date(y1, m1, d1) 

                            #compara a data atual com a data_prevista_leitura, se a data for maior que a atual, será a próxima leitura e seta a variável leitura_visualizada para true
                            if data_prevista_leitura > data_atual and leitura_visualizada == False:
                                self._state = data_prevista_leitura.strftime("%d/%m/%Y") #atualiza o valor do sensor com a data no formato brasileiro
                                leitura_visualizada = True

            else:
                self._state = 'Erro ao efetuar autenticação: ', soup.find('div', class_='textoErroMensagem')

