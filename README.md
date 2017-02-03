# EsiosData

***Web scraper* para datos de demanda, producción y coste de la energía eléctrica en España, y simulador de facturación eléctrica según el PVPC.**

Para utilizarlo necesitas obtener un `token` para la autentificación en la API de la web [ESIOS de REE](https://www.esios.ree.es/es).
* Envía un correo electrónico a [consultasios@ree.es](mailto:consultasios@ree.es?Subject=Solicitud%20de%20token%20personal) solicitando un código de acceso personal.
* Recibirás un código (`token`), grábalo en disco en tu `/home/user` como un archivo oculto de nombre `.token_api_esios`. En línea de comandos, ejecuta el siguiente comando substituyendo las X's por tu código personal: 
    ```
    echo "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" > ~/.token_api_esios
    ```

## Instalación
```
pip3 install esiosdata 
```

## Uso de la librería

### · Línea de comandos:
```
python esiosdata -h

>> usage: esiosdata [-h] [-v] [-d] [-fu] [-u] [-p] [-i [INFO [INFO ...]]]
>> 
>> Gestor de DB de PVPC/DEMANDA (esios.ree.es)
>> 
>> optional arguments:
>>   -h, --help            show this help message and exit
>>   -v, --verbose         Shows extra info
>>   -d, --dem             Select REE data
>>   -fu, -FU, --forceupdate
>>                         Force update of all available data
>>   -u, -U, --update      Updates data until today
>>   -p, --plot            Plots info of DB
>>   -i [INFO [INFO ...]], --info [INFO [INFO ...]]
>>                         Shows info of DB 
```

### · Python:

#### - Datos de PVPC:
```
from esiosdata import PVPC

pvpc_handler = PVPC()
print('Códigos de tarifas: {}'.format(pvpc_handler.tarifas))

ts_last, nrows_tot = pvpc_handler.last_entry()
print('TS LAST VALUE: {}; TOTAL VALUES: {}'.format(ts_last, nrows_tot))

from esiosdata.facturapvpc import (FacturaElec, ROUND_PREC, TIPO_PEAJE_GEN, TIPO_PEAJE_NOC, TIPO_PEAJE_VHC,
                                   ZONA_IMPUESTOS_CANARIAS, ZONA_IMPUESTOS_PENIN_BALEARES, ZONA_IMPUESTOS_CEUTA_MELILLA)

# Salida:

>> * BASE DE DATOS LOCAL HDF:
>> 	Nº entradas:	24913 mediciones
>> 	Última:     	01-02-2017 23:00
>> LA INFORMACIÓN ESTÁ ACTUALIZADA (delta = -34321.0 segs)
>> Códigos de tarifas: ['GEN', 'NOC', 'VHC']
>> TS LAST VALUE: 2017-02-01 23:00:00+01:00; TOTAL VALUES: 24913
```
Más detalles en el notebook asociado: "[esiosdata - PVPC data](https://github.com/azogue/esiosdata/blob/master/notebooks/esiosdata%20-%20PVPC%20data.ipynb)"

#### - Facturación del consumo eléctrico:

Este paquete incorpora una **calculadora de la factura eléctrica** en base a la legislación española sobre el **PVPC** (*Precio voluntario para el pequeño consumidor*). Facilita el cálculo del coste de la electricidad para las distintas discriminaciones horarias disponibles, tanto para lecturas de consumo totales (contadores antiguos) como para los nuevos contadores de registro horario.

La clase `FacturaElec` proporciona un objeto con el desglose detallado de cada periodo facturado, además de producir representaciones de dicho desglose en texto plano y HTML. 
```
from esiosdata import FacturaElec
t_0, t_f = '2016-11-01', '2016-12-31'
factura = FacturaElec(t_0, t_f, tipo_peaje='VHC', consumo=[219, 126, 154])
html_factura = factura.to_html()
print(factura)  # representación en texto plano

# Salida:

>> FACTURA ELÉCTRICA:
>> --------------------------------------------------------------------------------
>> * Fecha inicio             	01/11/2016
>> * Fecha final              	31/12/2016
>> * Peaje de acceso          	2.0DHS (Vehículo eléctrico)
>> * Potencia contratada      	3.45 kW
>> * Consumo periodo          	499.00 kWh
>> * ¿Bono Social?            	No
>> * Equipo de medida         	1.59 €
>> * Impuestos                	Península y Baleares (IVA)
>> * Días facturables         	60
>> --------------------------------------------------------------------------------
>> 
>> - CÁLCULO DEL TÉRMINO FIJO POR POTENCIA CONTRATADA:
>>     3.45 kW * 42.043426 €/kW/año * 60 días (2016) / 366 = 23.78 €
>>      -> Término fijo                                                   23.78 €
>> 
>> - CÁLCULO DEL TÉRMINO VARIABLE POR ENERGÍA CONSUMIDA (TARIFA 2.0DHS):
>>     Periodo 1: 0.151329 €/kWh                          -> 33.14€(P1)
>>     - Peaje de acceso: 219kWh * 0.062012€/kWh = 13.58€
>>     - Coste de la energía: 219kWh * 0.089317€/kWh = 19.56€
>>     Periodo 2: 0.080943 €/kWh                          -> 10.20€(P2)
>>     - Peaje de acceso: 126kWh * 0.002879€/kWh = 0.36€
>>     - Coste de la energía: 126kWh * 0.078064€/kWh = 9.84€
>>     Periodo 3: 0.062982 €/kWh                          -> 9.70€(P3)
>>     - Peaje de acceso: 154kWh * 0.000886€/kWh = 0.14€
>>     - Coste de la energía: 154kWh * 0.062096€/kWh = 9.56€
>>      -> Término de consumo                                             53.04 €
>> 
>> 
>> 
>> - IMPUESTO ELÉCTRICO:
>>     5.11269632% x (23.78€ + 53.04€)                                    3.93 €
>> 
>> - EQUIPO DE MEDIDA:                                                    1.59 €
>> 
>> - IVA O EQUIVALENTE:
>>     21% de 82.34€                                                      17.29 €
>> 
>> ################################################################################
>> # TOTAL FACTURA                                                        99.63 €
>> ################################################################################
```
Más detalles en el notebook asociado: "[esiosdata - Facturación](https://github.com/azogue/esiosdata/blob/master/notebooks/esiosdata%20-%20Facturación.ipynb)"

## Tests

Este paquete está testado con una cobertura completa (*100% code coverage*), y no se le han detectado errores, lo cual no es garantía de que no los haya. Si descubres alguno, que no esté relacionado con la respuesta de los servidores de ESIOS (que fallan a menudo y son algo perezosos, todo sea dicho), puedes descargar el paquete completo y ejecutar los tests, así como corregir el error!
```
py.test --cov=esiosdata -v --cov-report html
```
