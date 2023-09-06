'''
Version:
mie 30 ago 2023 18:00:50 CEST

= Enviar datos a nodeRed 
= consulta cada 5 min
=> Incluir logs
=> Es necesario pedir un nuevo key?
=> Asegurarse de que la consulta tiene el formato adecuado
=> Leer varias estaciones Huawei del .ini

'''

import sys
from datetime import datetime
import time
import requests;
import json;
import configparser
import paho.mqtt.publish as publish
import sched, threading
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from datetime import timedelta



HToken = ""

''' Niveles de logging
Para obtener _TODO_ el detalle: level=logging.INFO
Para comprobar los posibles problemas level=logging.WARNINg
Para comprobar el funcionamiento: level=logging.DEBUG
'''
logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler('./logs/log_datadis.log', maxBytes=10000000, backupCount=4)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
        

def mqtt_tx(client,s_value):
    # logging.debug(client + "  " + s_register + "  " + s_value)
    mqtt_topic_prefix = parser.get('mqtt_broker','mqtt_topic_prefix')
    mqtt_ip = parser.get('mqtt_broker','mqtt_ip')
    mqtt_login = parser.get('mqtt_broker','mqtt_login')
    mqtt_password = parser.get('mqtt_broker','mqtt_password')

    mqtt_auth = { 'username': mqtt_login, 'password': mqtt_password }
    response = publish.single(mqtt_topic_prefix + "/" + client, s_value, hostname=mqtt_ip, auth=mqtt_auth)
    # logging.info( mqtt_ip + " -> " + mqtt_topic_prefix + "/" + client + "  " + s_value)
    logging.info( mqtt_ip + " -> " + mqtt_topic_prefix + "/"  + client + "  " + str(s_value))

def pedir_nuevo_key():

    # logging.debug('El Key no se ha obtenido en el ultimo periodo. Pedimos un nuevo key')
    huawei_login = parser.get('huawei_server','huawei_login')
    huawei_password = parser.get('huawei_server','huawei_password')
    urlOpenApiHuawei_login = "https://intl.fusionsolar.huawei.com/thirdData/login"
    headers = {'content-type': 'application/json'}
    json_req_body = '{"userName":"'+huawei_login+'", "systemCode":"'+huawei_password+'" }';
    
    logging.debug("headers:");
    logging.debug(headers);
    logging.debug("json_req_body:");
    logging.debug(json_req_body);
    
    ''' Componemos y ejecutamos la peticion '''
    requestResponse = requests.post(urlOpenApiHuawei_login, data = json_req_body, headers=headers);

    # Obtenemos el codigo del estado devuelto por la peticion
    requestResponseStatus = requestResponse.status_code
    logging.debug("__La respuesta obtenida:")
    logging.debug(requestResponse)
    global HToken
    HToken = requestResponse.cookies.get("XSRF-TOKEN")
    logging.debug("XSRF-TOKEN:")
    logging.debug(type(HToken))
    logging.debug(HToken)


# 
parser = configparser.ConfigParser()
parser.read('config_huawei_server.ini')
pedir_nuevo_key()
logging.debug(HToken)

# param_stationCodes = parser.get('huawei_inversor','stationCodes')
# inversorName = parser.get('huawei_inversor','name')



def serverReading(tm):
    threading.Timer(tm, serverReading,args=[tm]).start()
    logging.debug("*" * 4 + ' serverReading')

    # pedir_nuevo_key()

    global HToken

    ''' Construimos los componentes de la peticion '''
    param_stationCodes = parser.get('huawei_inversor','stationCodes')
    inversorName = parser.get('huawei_inversor','name')

    urlOpenApiHuawei_getDevRealKpi = "https://intl.fusionsolar.huawei.com/thirdData/getStationRealKpi"
    headers = {'content-type': 'application/json', 'XSRF-TOKEN': ''+ HToken + ''}

    json_req_body = "{\"stationCodes\" : \""
    json_req_body += param_stationCodes
    json_req_body +="\"}"

    # logging.debug("headers:");
    # logging.debug(headers);
    logging.debug("json_req_body:");
    logging.debug(json_req_body);


    try:
        ''' Componemos y ejecutamos la peticion '''
        
        requestResponse = requests.post(urlOpenApiHuawei_getDevRealKpi, data = json_req_body, headers=headers);
        requestResponseStatus = requestResponse.status_code
        #logging.debug("Codigo respuesta: ",requestResponseStatus);
        if requestResponseStatus==200:
            responseJson = json.loads(requestResponse.text)
            logging.debug(responseJson)
            r_value = responseJson['data'][0]["dataItemMap"]['total_power'] # received value
            logging.info('totalEnergy: ' + str(r_value))
            mqtt_tx(inversorName,r_value)

    except Exception as ex:

        logging.info ("ERROR: LA EJECUCION NO HA TERMINADO CORRECTAMENTE DEBIDO A UN ERROR");
        logging.info (ex);

serverReading(300.0)

    


    
