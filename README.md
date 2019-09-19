# Home Assistant Custom Components
Componentes personalizados para o Home Assistant

## Component Overview
- Green Card component

## Green Card
> NOTA: Esse componente funciona apenas para pessoas que utilizam o sistema de cartão "Green Card" (https://www.grupogreencard.com.br/)

### Instalação - Installation

- Copie o diretório "green_card" para a pasta <config dir>/custom_components.
- Configure um sensor com a configuração abaixo.
- Reinicie p Home Assistant.

Deve ficar semelhante a estrutura abaixo após a instalação:
.homeassistant/
|-- custom_components/
|   |-- green_card/
|       |-- __init__.py
|       |-- sensor.py

### Utilizar - Usage
Para usar esse componente em sua instalação, adicione o seguinte código no seu arquivo configuration.yaml:

#### Exemplo de configuração configuration.yaml - Example configuration.yaml entry

```
sensor:
  - platform: green_card
    name: Saldo GreenCard
    cpf: "000.000.000-00"  
    senha: Coloque sua senha aqui
```

As credenciais de acesso devem ser as mesmas credenciais utilizadas na página de autenticação do site [Green Card - Login](https://www.grupogreencard.com.br/sysweb/site/loga_usuario) 

### Captura de tela - Screenshot
![Sensor GreenCard](https://github.com/dougbaptista/custom_components/blob/master/screenshots/green_card.jpg?raw=true)

### Créditos - Credits
- [@willsilvano](https://github.com/willsilvano) - Por realizar toda lógica de consultar as informações do site, só adaptei para criar um sensor no HA.
