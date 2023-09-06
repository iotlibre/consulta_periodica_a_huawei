'''
Version:
v4

mie 06 sep 2023 07:23:17 CEST
v2
Request cada 5 min
Funciona pidiendo un nuevo key despues de cada request


= Enviar datos a nodeRed 
= consulta cada 5 min
= Incluir logs
= Es necesario pedir un nuevo key?
=> Asegurarse de que la consulta tiene el formato adecuado
=> Leer varias estaciones Huawei del .ini

'''

import sys
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
lastTimeKey = datetime.now()

''' Niveles de logging
Para obtener _TODO_ el detalle: level=logging.INFO
Para comprobar los posibles problemas level=logging.WARNINg
Para comprobar el funcionamiento: level=logging.DEBUG
'''
logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler('./logs/log_datadis.log', maxBytes=1000000, backupCount=4)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
        

def mqtt_tx(client,s_value):

    mqtt_topic_prefix = parser.get('mqtt_broker','mqtt_topic_prefix')
    mqtt_ip = parser.get('mqtt_broker','mqtt_ip')
    mqtt_login = parser.get('mqtt_broker','mqtt_login')
    mqtt_password = parser.get('mqtt_broker','mqtt_password')
    mqtt_auth = { 'username': mqtt_login, 'password': mqtt_password }
    publish.single(mqtt_topic_prefix + "/" + client, s_value, hostname=mqtt_ip, auth=mqtt_auth)
    logging.info( mqtt_ip + " -> " + mqtt_topic_prefix + "/"  + client + "  " + str(s_value))

def pedir_nuevo_key():

    huawei_login = parser.get('huawei_server','huawei_login')
    huawei_password = parser.get('huawei_server','huawei_password')
    urlOpenApiHuawei_login = "https://intl.fusionsolar.huawei.com/thirdData/login"
    headers = {'content-type': 'application/json'}
    json_req_body = '{"userName":"'+huawei_login+'", "systemCode":"'+huawei_password+'" }';
    
    logging.debug("headers:");
    logging.debug(headers);
    logging.debug("json_req_body:");
    logging.debug(json_req_body);
    
    requestResponse = requests.post(urlOpenApiHuawei_login, data = json_req_body, headers=headers);
    requestResponseStatus = requestResponse.status_code

    logging.debug("__Respuesta de la peticion XSRF-TOKEN:")
    logging.debug(requestResponse)
    global HToken
    HToken = requestResponse.cookies.get("XSRF-TOKEN")
    logging.debug("XSRF-TOKEN:")
    logging.debug(type(HToken))
    logging.info(HToken)

def nedNewKey():
    global lastTimeKey
    needed = False
    current = datetime.now()
    treinta = timedelta(minutes = 12)
    logging.debug("__nedNewKey ?")
    logging.debug(str(current))
    logging.debug(str(lastTimeKey + treinta))
   
    if (current > (lastTimeKey + treinta)):
        needed = True
        lastTimeKey = current

    logging.debug(needed)
    return needed
        

def serverReading(tm):
    threading.Timer(tm, serverReading,args=[tm]).start()
    logging.debug("_" * 2 + ' serverReading')

    global HToken
    logging.debug(HToken)

    ''' Construimos los componentes de la peticion '''
    param_stationCodes = parser.get('huawei_inversor','stationCodes')
    inversorName = parser.get('huawei_inversor','name')

    try:
        urlOpenApiHuawei_getDevRealKpi = "https://intl.fusionsolar.huawei.com/thirdData/getStationRealKpi"
        headers = {'content-type': 'application/json', 'XSRF-TOKEN': ''+ HToken + ''}

        json_req_body = "{\"stationCodes\" : \""
        json_req_body += param_stationCodes
        json_req_body +="\"}"

        # logging.debug("headers:");
        # logging.debug(headers);
        logging.debug("json_req_body:");
        logging.debug(json_req_body);

    
        ''' Componemos y ejecutamos la peticion '''
        
        requestResponse = requests.post(urlOpenApiHuawei_getDevRealKpi, data = json_req_body, headers=headers);
        requestResponseStatus = requestResponse.status_code
        #logging.debug("Codigo respuesta: ",requestResponseStatus);
        if requestResponseStatus==200:
            responseJson = json.loads(requestResponse.text)
            logging.debug("responseJson:")
            logging.debug(responseJson)
            r_value = responseJson['data'][0]["dataItemMap"]['total_power'] # received value
            logging.info('totalEnergy: ' + str(r_value))
            mqtt_tx(inversorName,r_value)

    except Exception as ex:

        logging.info ("ERROR: LA EJECUCION NO HA TERMINADO CORRECTAMENTE DEBIDO A UN ERROR");
        logging.info (ex);

    if nedNewKey():
        pedir_nuevo_key()

parser = configparser.ConfigParser()
parser.read('config_huawei_server.ini')
pedir_nuevo_key()
logging.debug(HToken)
serverReading(300.0)

    


    
