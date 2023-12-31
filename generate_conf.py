"""This script generates conf.yaml file from csv file.

CSV file format:
====================
key1,key2,key3
instance1_value1,instance1_value2,instance1_value3
instance2_value1,instance2_value2,instance2_value3
====================

====================
ip_address,username,password,port,min_collection_interval
10.0.0.1,<username>,<password>,8080,120
10.0.0.2,<username>,<password>,8080,120
====================

Command usage:
    python generate_conf.py dell_emc_isilon.csv
    python generate_conf.py netapp_ontap.csv
    /opt/datadog-agent/embedded/bin/python generate_conf.py dell_emc_isilon.csv
    /opt/datadog-agent/embedded/bin/python generate_conf.py netapp_ontap.csv


Note:
- Make sure the CSV file is in the mentioned format only, without unnecessary whitespaces and commas.
- Number of values must match the number of keys at the header and in the same order.
"""

import csv
import json
import sys

import yaml

SCRIPT_INDICATORS = "=" * 50
MULTIVALUE = ["tags"]

# start of the script
print("\n" + SCRIPT_INDICATORS)


# run to exit from script
def exit():
    print(SCRIPT_INDICATORS + "\n")
    sys.exit()


# convert value using given function
def conversion(value: str, convertor: callable):
    try:
        return convertor(value)
    except (ValueError, TypeError):
        return


def to_bool(value: str):
    if value.lower() in ["true", "t", "y", "yes", "on"]:
        return True
    if value.lower() in ["false", "f", "n", "no", "off"]:
        return False


# convert value to suitable type if possible
def convert(value: str):
    if not isinstance(value, str):
        return value
    value = value.strip()
    _int = conversion(value, int)
    if _int is not None:
        return _int
    _float = conversion(value, float)
    if _float is not None:
        return _float
    _bool = conversion(value, to_bool)
    if _bool is not None:
        return _bool

    return value


# convert comma-separate value to list
def convert_list(value: str):
    return [ele.strip() for ele in value.split(",") if ele.strip()]


# check if file path argument is provided or not
if len(sys.argv) < 2:
    print("[ERROR] Please enter the file name in the command for input.")
    exit()


# initial empty configuration dictionary
conf = {"init_config": {}, "instances": []}

# read the configurations from csv file
try:
    csv_reader = csv.DictReader(open(sys.argv[1]))
except FileNotFoundError:
    print(f"[ERROR] Please check the file name and path, provided file '{sys.argv[1]}' does not exist.")
    exit()
instances = list(csv_reader)
new_instances = []
for instance in instances:
    new_instances.append({k: (convert(v) if k not in MULTIVALUE else convert_list(v)) for k, v in instance.items()})
conf["instances"] = new_instances
print(f"[INFO] Converted configuration content...\n{json.dumps(conf, indent=4)}\n")

# dump the final configuration to conf.yaml file
conf_yaml = yaml.dump(conf, default_style=False, indent=2, sort_keys=False)
conf_yaml = "\t" + conf_yaml.replace("\n", "\n\t")
print(f"[INFO] Generated conf.yaml content...\n{conf_yaml}")
print("[INFO] conf.yaml is saved in current directory")
yaml.dump(conf, open("conf.yaml", "w"), default_style=None, indent=2, sort_keys=False)

# end of the script
print(SCRIPT_INDICATORS + "\n")
