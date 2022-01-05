#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import remove, path
from colorama import Fore, Style
from datetime import datetime, timedelta, date
import mysql.connector
import argparse
import json
from tabulate import tabulate

switcher = {
    "b": "boolean",
    "e": "enum",
    "d": "double",
    "f": "float",
    "l": "long",
    "s": "short",
    "o": "octet",
    "D": "DoubleArray1D",
    "F": "FloatArray1D",
    "L": "LongArray1D",
    "S": "ShortArray1D",
    "O": "OctetArray1D",
    "0": "0",
    "9": "DoubleArray2D",
    "8": "FloatArray2D",
    "7": "LongArray2D",
    "6": "ShortArray2D",
    "5": "OctetArray2D"
}

def configurationFormat(description, unit, magnitude_values, type, upper_limit, lower_limit, default_sampling_period, default_storage_period, dimension_y, dimension_x):
    contentMonitor = {}
    valueNode = {}
    heightNode = {}
    widhtNode = {}

    contentMonitor = {
        "description": description,
        "units": unit,
        "type": type,
        "upper_limit": upper_limit,
        "lower_limit": lower_limit,
        "default_sampling_period": default_sampling_period,
        "default_storage_period": default_storage_period,
    }

    if type == "boolean" or type == "enum":
        valueNode = {"value": magnitude_values}
        contentMonitor.update(valueNode)
    if dimension_y != 1 and dimension_y != "None":
        heightNode = {"height": dimension_y}
        contentMonitor.update(heightNode)
    if dimension_x != 1 and dimension_x != "None":
        widhtNode = {"widht": dimension_x}
        contentMonitor.update(widhtNode)

    return contentMonitor

def sqlErrors(error):
    if error:
        if error.errno:
            print("Error code:", error.errno)
        if error.sqlstate:
            print("SQLSTATE:", error.sqlstate)
        if error.msg:
            print("Message:", error.msg)

#######################################
# Conexión con la base de datos
#######################################
def init():
    try:
        print("Conectando con %s..." % 'calp-ltdb')
        db_connection = mysql.connector.connect(
            host='*****',
            user='*****',
            passwd='*****',
            database='*****'
        )
        if db_connection.is_connected():
            db_info = db_connection.get_server_info()
            print("Connected to MySQL Server version ", db_info)

            getComponents = db_connection.cursor(buffered=True)
            getComponents.execute("select id as component_id, name, className from monitor_component limit 50;")
            result = getComponents.fetchall()

            json_data = []
            content = {}
            i = 0

            for (component_id, name, className) in result:
                content = {
                    "instance": name,
                    "className": className,
                    "monitors": {}
                }
                print("get component ---> " + str(i))

                #### ------ ------ ------ ------ ------ ------  Monitor_description ------ ------ ------ ------ ------  ####

                getMonitors = db_connection.cursor()
                getMonitors.execute("select monitor.* from monitor_description monitor "
                                    "where monitor.version IN ("
                                    "select MAX(monitor2_.version) "
                                    "from monitor_description monitor2_ "
                                    "where monitor.magnitude like binary monitor2_.magnitude "
                                    "AND monitor.id_monitor_component = monitor2_.id_monitor_component "
                                    "and monitor2_.id_monitor_component = "+ str(component_id) +" "
                                    "group by monitor2_.id_monitor_component,monitor2_.magnitude) "
                                    "group by id_monitor_component, magnitude;")
                resultmonitor = getMonitors.fetchall()

                for (monitor_id, id_monitor_component, magnitude, version, unit, type, dimension_x, dimension_y, description) in resultmonitor:
                    print("get monitor --> " + str(i))
                    getMonitorsConfig = db_connection.cursor()
                    getMonitorsConfig.execute("select id as id_conf, storage_period, propagate_period, id_monitor_description, id_monitor_configuration "
                                              "from monitor_config "
                                              "where id_monitor_description =" + str(monitor_id) + " "
                                              "and id_monitor_configuration = 1;")
                    resultmonitorConfig = getMonitorsConfig.fetchall()

                    for (id_conf, storage_period, propagate_period, id_monitor_description, id_monitor_configuration) in resultmonitorConfig:
                        print("get config -> " + str(i))
                        default_sampling_period = str(propagate_period)
                        default_storage_period = str(storage_period)

                        getMonitorsRange = db_connection.cursor()
                        getMonitorsRange.execute("select max, min "
                                                 "from monitor_range "
                                                 "where id_monitor_config = " + str(id_conf) + ";")
                        resultmonitorRange = getMonitorsRange.fetchall()

                        countDivider_y = 1
                        countDivider_x = 1

                        if dimension_x == 1 and dimension_y == 1:
                            upper_limit = ""
                            lower_limit = ""
                        else:
                            upper_limit = "["
                            lower_limit = "["

                        if resultmonitorRange.__len__() == 0:
                            upper_limit = "0"
                            lower_limit = "0"
                        else:
                            for max, min in resultmonitorRange:
                                if dimension_x == 1 and dimension_y == 1:
                                    upper_limit = str(max)
                                    lower_limit = str(min)
                                elif countDivider_x == dimension_x and countDivider_y == dimension_y:
                                    if countDivider_x > 1 or countDivider_y > 1:
                                        upper_limit += str(max) + "]"
                                        lower_limit += str(min) + "]"
                                    else:
                                        upper_limit += str(max)
                                        lower_limit += str(min)
                                else:
                                    if countDivider_x == dimension_x:
                                        upper_limit += str(max) + ";"
                                        lower_limit += str(min) + ";"
                                        countDivider_x = 1
                                        countDivider_y = countDivider_y + 1
                                    else:
                                        upper_limit += str(max) + ","
                                        lower_limit += str(min) + ","
                                        countDivider_x = countDivider_x + 1
                    #
                    # set monitor data configuration
                    #
                    gettype = switcher.get(type)
                    setformat = configurationFormat(description, unit, "None", gettype, upper_limit, lower_limit, default_sampling_period, default_storage_period, dimension_y, dimension_x)
                    content['monitors'][magnitude] = (setformat)

                #### ------ ------ ------ ------ ------ ------  Magnitude_description ------ ------ ------ ------ ------  ####

                getMagnitudes = db_connection.cursor()
                getMagnitudes.execute("select magnitude, type, id_magnitude_type from magnitude_description monitor "
                                      "where monitor.version IN ("
                                      "select MAX(monitor2_.version) "
                                      "from magnitude_description monitor2_ "
                                      "where monitor.magnitude like binary monitor2_.magnitude "
                                      "AND monitor.id_monitor_component = monitor2_.id_monitor_component "
                                      "and monitor2_.id_monitor_component = "+ str(component_id) +" "
                                      "group by monitor2_.id_monitor_component,monitor2_.magnitude) "
                                      "group by id_monitor_component, magnitude;")
                resultMagnitudes = getMagnitudes.fetchall()

                for (magnitude, type, id_magnitude_type) in resultMagnitudes:
                    getMagnitudeValues = db_connection.cursor()
                    getMagnitudeValues.execute("select name "
                                               "from magnitude_value "
                                               "where id_magnitude_type = " + str(id_magnitude_type) + " ")
                    resultMagnitudesValues = getMagnitudeValues.fetchall()

                    magnitude_values = ""
                    count_magnitude_values = 1
                    for (name) in resultMagnitudesValues:
                        arrangeName = "%s" % name
                        if count_magnitude_values == resultMagnitudesValues.__len__():
                            magnitude_values += str(arrangeName)
                            count_magnitude_values = 0
                        else:
                            magnitude_values += str(arrangeName) + ", "
                            count_magnitude_values = count_magnitude_values + 1
                    #
                    # set magnitude data configuration
                    #
                    gettype = switcher.get(type)
                    setformat = configurationFormat("None", "None", magnitude_values, gettype, "true", "false", "0.0", "0.0", "None", "None")
                    content['monitors'][magnitude] = (setformat)

                json_data.append(content)
                content = {}
                i = i + 1

            stud_json = json.dumps(json_data, indent=2)
            print("results: ", stud_json)

            with open('output.json', 'w') as file:
                json.dump(json_data, file)

            getComponents.close()
            getMonitors.close()
            getMonitorsConfig.close()
            getMonitorsRange.close()
            getMagnitudes.close()
            getMagnitudeValues.close()
            db_connection.close()

    except mysql.connector.Error as e:
        sqlErrors(e)
    except Exception as e:
        print(e)
    finally:
        if db_connection.is_connected():
            getComponents.close()
            getMonitors.close()
            getMonitorsConfig.close()
            getMonitorsRange.close()
            getMagnitudes.close()
            getMagnitudeValues.close()
            db_connection.close()
            print("Finalizando conexión con %s..." % 'calp-ltdb')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    try:
        init()
    except Exception as error:
        print(error)
        quit()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
