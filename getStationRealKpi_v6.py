'''
Version:
vie 08 sep 2023 06:52:00 CEST
V6
url consulta en .ini
+ robusto
V5
Consulta a varios inversores
v4
Consulta con key nuevo cada 30 minutos
Probado con credenciales erroneas
v2
Request cada 5 min
Funciona pidiendo un nuevo key despues de cada request

= Enviar datos a nodeRed 
= consulta cada 5 min
= Incluir logs
= Es necesario pedir un nuevo key?
= Asegurarse de que la consulta tiene el formato adecuado
= Leer varias estaciones Huawei del .ini

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
last_time_key = datetime.now()

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
    logging.info("__mqtt_tx")
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
    huawei_domain = parser.get('huawei_server','huawei_domain')
    
    # "https://intl.fusionsolar.huawei.com/thirdData/login"
    url_login = "https://"
    url_login += huawei_domain
    url_login += "/thirdData/login"

    headers = {'content-type': 'application/json'}
    json_req_body = '{"userName":"'+huawei_login+'", "systemCode":"'+huawei_password+'" }'
    
    logging.debug("headers:")
    logging.debug(headers)
    logging.debug("json_req_body:")
    logging.debug(json_req_body)
    
    requestResponse = requests.post(url_login, data = json_req_body, headers=headers);
    requestResponseStatus = requestResponse.status_code

    logging.debug("__Respuesta de la peticion XSRF-TOKEN:")
    logging.debug(requestResponse)
    global HToken
    HToken = requestResponse.cookies.get("XSRF-TOKEN")
    logging.info("XSRF-TOKEN:")
    logging.debug(type(HToken))
    logging.info(HToken)

def need_new_key():
    global last_time_key
    needed = False
    current = datetime.now()
    # El bucle de consultas es cada 5 min
    # Peticion de key a los 25 minutos (consulta pasados los 22)
    # La consulta de la energia será a la siguiente (a los 30 min)
    treinta = timedelta(minutes = 12)
    logging.debug("__need_new_key ?")
    logging.debug(str(current))
    logging.debug(str(last_time_key + treinta))
   
    if (current > (last_time_key + treinta)):
        needed = True
        last_time_key = current

    logging.debug(needed)
    return needed
        
def serverReading(tm):
    threading.Timer(tm, serverReading,args=[tm]).start()
    global HToken
    huawei_domain = parser.get('huawei_server','huawei_domain')

    logging.debug("_" * 2 + ' serverReading')
    logging.debug(HToken)

    param_stationCodes = parser.get('huawei_inversor','stationCodes')

    # "https://intl.fusionsolar.huawei.com/thirdData/getStationRealKpi"
    url_dev_real = "https://"
    url_dev_real += huawei_domain
    url_dev_real += "/thirdData/getStationRealKpi"

    headers = {'content-type': 'application/json', 'XSRF-TOKEN': ''+ HToken + ''}

    json_req_body = "{\"stationCodes\" : \""
    json_req_body += param_stationCodes
    json_req_body +="\"}"

    # logging.debug("headers:");
    # logging.debug(headers);
    logging.debug("json_req_body:")
    logging.debug(json_req_body)
    # La consulta al servidor
    requestResponse = requests.post(url_dev_real, data = json_req_body, headers=headers);
    requestResponseStatus = requestResponse.status_code
    
    try:
        if requestResponseStatus==200:
            responseJson = json.loads(requestResponse.text)
            logging.debug("responseJson:")
            logging.debug(responseJson)
            r_list = responseJson['data']
            logging.debug("type r_list:")
            logging.debug(type(r_list))

            for r_station in r_list:
                logging.info(r_station)
                r_name = r_station["stationCode"] # received name
                r_value = r_station["dataItemMap"]['total_power'] # received value
                logging.info('stationCode: ' + str(r_name))
                logging.info('totalEnergy: ' + str(r_value))
                mqtt_tx(r_name,r_value)

    except Exception as ex:
        logging.info ("ERROR: LA EJECUCION NO HA TERMINADO CORRECTAMENTE DEBIDO A UN ERROR");
        logging.info (ex);

    if need_new_key():
        pedir_nuevo_key()

parser = configparser.ConfigParser()
parser.read('config_huawei_server.ini')
pedir_nuevo_key()
logging.debug(HToken)
serverReading(300.0)

    


    
