'''
Version: lun 28 ago 2023 08:28:47 CEST
'''

import sys
from datetime import datetime
import time
import requests
import json
import configparser



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

parser = configparser.ConfigParser()
parser.read('config_huawei_server.ini')
pedir_nuevo_key()
print(HToken)


try:

    param_XSRF_TOKEN = HToken

    ''' Construimos los componentes de la peticion '''
    urlOpenApiHuawei_getDevRealKpi = "https://intl.fusionsolar.huawei.com/thirdData/stations"
    headers = {'content-type': 'application/json', 'XSRF-TOKEN': ''+ param_XSRF_TOKEN + ''}
    json_req_body = '{"pageNo": 1}'

    # print("headers:");
    # print(headers);
    # print("json_req_body:");
    # print(json_req_body);
    
    ''' Componemos y ejecutamos la peticion '''
    requestResponse = requests.post(urlOpenApiHuawei_getDevRealKpi, data = json_req_body, headers=headers);

    # Obtenemos el codigo del estado devuelto por la peticion
    requestResponseStatus = requestResponse.status_code
    #print("Codigo de la respuesta obtenido:");
    print(requestResponseStatus);

    if requestResponseStatus==200:

        print("----");
        print("Respuesta recibida del servidor:");
        print(requestResponse.text);
        print("----");

except Exception as ex:

    print ("-----------");
    print ("ERROR: LA EJECUCION NO HA TERMINADO CORRECTAMENTE DEBIDO A UN ERROR");
    print (ex);
    print ("-----------");

    
  

    


    
