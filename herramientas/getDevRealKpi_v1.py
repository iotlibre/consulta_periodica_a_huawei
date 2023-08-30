'''
Version: lun 28 ago 2023 08:28:47 CEST
'''

import sys
from datetime import datetime
import time
import requests;
import json;
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



# 
parser = configparser.ConfigParser()
parser.read('config_huawei_server.ini')
pedir_nuevo_key()
print(HToken)


try:


    # param_devTypeId = "38"
    # param_sns = "210107380110K4000347"

    param_devTypeId = parser.get('huawei_inversor','devTypeId')
    param_sns = parser.get('huawei_inversor','sns')
    param_XSRF_TOKEN = HToken


    ''' Construimos los componentes de la peticion '''
    urlOpenApiHuawei_getDevRealKpi = "https://intl.fusionsolar.huawei.com/thirdData/getDevRealKpi"
    headers = {'content-type': 'application/json', 'XSRF-TOKEN': ''+ param_XSRF_TOKEN + ''}
    # json_req_body = '{"devTypeId":"'+param_devTypeId+'" }'
    # json_req_body = '{"devIds":"'+param_devIds+'", "devTypeId":"'+param_devTypeId+'" }'
    json_req_body = '{"sns":"'+param_sns+'", "devTypeId":"'+param_devTypeId+'" }'

    # print("headers:");
    # print(headers);
    # print("json_req_body:");
    # print(json_req_body);
    
    ''' Componemos y ejecutamos la peticion '''
    requestResponse = requests.post(urlOpenApiHuawei_getDevRealKpi, data = json_req_body, headers=headers);

    # Obtenemos el codigo del estado devuelto por la peticion
    requestResponseStatus = requestResponse.status_code;
    #print("Codigo de la respuesta obtenido:");
    #print(requestResponseStatus);

    if requestResponseStatus==200:

        print("----");
        print("Respuesta recibida del servidor:");
        print(requestResponse.text);
        print("----");


        ''' Manejamos la respuesta JSON '''
        #json_data = json.loads(requestResponse.text);

        ''' Obtenemos el token de autentificacion '''
        #json_data_body = json_data["data"][0];
        #json_data_body_dataItemMap = json_data_body["dataItemMap"];
        #json_data_body_data_activePower = json_data_body_dataItemMap["active_power"];
        #print("Active power: " + str(json_data_body_data_activePower));
        #print(json_data_body_data_activePower);
   

except Exception as ex:

    print ("-----------");
    print ("ERROR: LA EJECUCION NO HA TERMINADO CORRECTAMENTE DEBIDO A UN ERROR");
    print (ex);
    print ("-----------");

    
  

    


    
