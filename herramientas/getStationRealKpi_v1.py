'''
Version:
mie 30 ago 2023 07:15:06 CEST

=> Enviar datos a nodeRed 
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


def mqtt_tx(client,s_value):
    # logging.debug(client + "  " + s_register + "  " + s_value)
    # Parseo de las variables
    mqtt_topic_prefix = parser.get('mqtt_broker','mqtt_topic_prefix')
    mqtt_ip = parser.get('mqtt_broker','mqtt_ip')
    mqtt_login = parser.get('mqtt_broker','mqtt_login')
    mqtt_password = parser.get('mqtt_broker','mqtt_password')

    mqtt_auth = { 'username': mqtt_login, 'password': mqtt_password }
    response = publish.single(mqtt_topic_prefix + "/" + client, s_value, hostname=mqtt_ip, auth=mqtt_auth)


def pedir_nuevo_key():

    # logging.debug('El Key no se ha obtenido en el ultimo periodo. Pedimos un nuevo key')
    huawei_login = parser.get('huawei_server','huawei_login')
    huawei_password = parser.get('huawei_server','huawei_password')
    ''' Construimos los componentes de la peticion '''
    urlOpenApiHuawei_login = "https://intl.fusionsolar.huawei.com/thirdData/login";
    headers = {'content-type': 'application/json'}
    json_req_body = '{"userName":"'+huawei_login+'", "systemCode":"'+huawei_password+'" }';

    
    print("headers:");
    print(headers);
    print("json_req_body:");
    print(json_req_body);
    
    ''' Componemos y ejecutamos la peticion '''
    requestResponse = requests.post(urlOpenApiHuawei_login, data = json_req_body, headers=headers);

    # Obtenemos el codigo del estado devuelto por la peticion
    requestResponseStatus = requestResponse.status_code
    print("Codigo de la respuesta obtenido:")
    print(requestResponseStatus)
    global HToken
    HToken = requestResponse.cookies.get("XSRF-TOKEN")
    print("XSRF-TOKEN:")
    print(type(HToken))
    print(HToken)




# 
parser = configparser.ConfigParser()
parser.read('config_huawei_server.ini')
pedir_nuevo_key()
print(HToken)


try:


    # param_devTypeId = "38"
    # param_sns = "210107380110K4000347"

    # param_devTypeId = parser.get('huawei_inversor','devTypeId')
    param_stationCodes = parser.get('huawei_inversor','stationCodes')
    inversorName = parser.get('huawei_inversor','name')
    param_XSRF_TOKEN = HToken

    ''' Construimos los componentes de la peticion '''
    # urlOpenApiHuawei_getDevRealKpi = "https://intl.fusionsolar.huawei.com/thirdData/getDevRealKpi"
    urlOpenApiHuawei_getDevRealKpi = "https://intl.fusionsolar.huawei.com/thirdData/getStationRealKpi"
    headers = {'content-type': 'application/json', 'XSRF-TOKEN': ''+ param_XSRF_TOKEN + ''}

    json_req_body = '{"stationCodes" : "AFD78D01047B420F9B1520F5E55575A6"}'
    print("json_req_body:");
    print(json_req_body);

    json_req_body = "{\"stationCodes\" : \""
    json_req_body += param_stationCodes
    json_req_body +="\"}"

    # print("headers:");
    # print(headers);
    print("json_req_body:");
    print(json_req_body);
    
    ''' Componemos y ejecutamos la peticion '''
    requestResponse = requests.post(urlOpenApiHuawei_getDevRealKpi, data = json_req_body, headers=headers);

    # Obtenemos el codigo del estado devuelto por la peticion
    requestResponseStatus = requestResponse.status_code
    #print("Codigo de la respuesta obtenido:");
    #print(requestResponseStatus);

    if requestResponseStatus==200:

        print("----")
        print("Respuesta recibida del servidor:")
        print(requestResponse.text);
        print("----")
        responseJson = json.loads(requestResponse.text)
        print(responseJson)
        print("----")
        print(responseJson['data'])
        print("----")
        print(responseJson['data'][0])
        print("----")
        print(responseJson['data'][0]["dataItemMap"])
        print("----")

        r_value = responseJson['data'][0]["dataItemMap"]['total_power'] # received value

        print('totalEnergy: ', r_value)
   
        mqtt_tx(inversorName,r_value)


   

except Exception as ex:

    print ("-----------");
    print ("ERROR: LA EJECUCION NO HA TERMINADO CORRECTAMENTE DEBIDO A UN ERROR");
    print (ex);
    print ("-----------");

    
  

    


    
