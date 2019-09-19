# custom_components
Custom components for home assistant (Componentes personalizados para o Home Assistant)

Some of my custom components for home-assistant. (http://www.home-assistant.io)

## Component Overview
- Green Card component

## Green Card
NOTA: Esse componente funciona apenas para pessoas que utilizam o sistema de cartão "Green Card" (https://www.grupogreencard.com.br/)
NOTE: This component only works for people using the "Green Card" card system (https://www.grupogreencard.com/)

### Instalação - Installation

- Copie o diretório "green_card" para a pasta <config dir>/custom_components.
- Configure um sensor com a configuração abaixo.
- Reinicie p Home Assistant.

### Utilizar - Usage
Para usar esse componente em sua instalação, adicione o seguinte código no seu arquivo configuration.yaml:

# Example configuration.yaml entry

sensor:
  - platform: green_card
    name: Saldo GreenCard
    cpf: "000.000.000-00"  
    senha: Coloque sua senha aqui
    
As credenciais de acesso devem ser as mesmas credenciais utilizadas na página de autenticação do site Green Card (https://www.grupogreencard.com.br/sysweb/site/loga_usuario) 
