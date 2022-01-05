# monitor manager database configurations file

#### Notas:
- **Magnitude_description**:
    - El campo "description" no esta en la base de datos pero si en los demás. Por ahora el campo es agregado colocado a "None" por defecto.
    - De igual forma los campos upper_limit, lower_limit, default_storage_period y default_sampling_period son colocados a "true", "false", "0.0", "0.0" por defecto respectivamente.
    - El campo "value" no esta en el .profile pero si en los demás.
- **Monitor_description**:
  - El script hace el siguiente arreglo siguiendo el formato establecido \
  En el upper_limit y el lower_limit cuando los elementos de un monitor array son todos iguales los agrupa en uno solo \
  ejemplo: \
    desigual: array["1000", "1000", "23", "1000"]..   result => "upper_limit": "["1000","1000", "1000", "23", "1000"]" \
    igual:    array["1000", "1000", "1000", "1000"].. result => "upper_limit": "["1000"]"


#### *- El script actualmente genera la siguiente vista de los datos de los monitores con el formato predefinido:

### monitor_description:

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
  
### magnitude_description:

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
