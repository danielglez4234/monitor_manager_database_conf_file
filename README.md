# monitor manager database configurations file

el script actualmente genera la siguiente vista para la visualización de los datos de los monitores con el formato predefinido para 'monitor_description' y 'magnitude_description'

### monitor_description

    "instance": <component_name>,
    "className": <class_name>,
    "monitors": {
      <monitor_name>: {
        "description": <description>,
        "units": <unit>,
        "type": <type>,
        "upper_limit": <upper_limit>,
        "lower_limit": <lower_limit>,
        "default_sampling_period": <default_sampling_period>,
        "default_storage_period": <default_storage_period>
      }
    }
  }
  
### magnitude_description

    "instance": <component_name>,
    "className": <class_name>,
    "monitors": {
      <monitor_name>: {
        "description": "None",
        "units": "None",
        "type": <type>,
        "upper_limit": "true",
        "lower_limit": "false",
        "default_sampling_period": "0.0",
        "default_storage_period": "0.0",
        "value": <values>
      }
    }
