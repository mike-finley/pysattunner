1. [Overview](#overview)
2. [API](#api)
    1. [SNMP](#snmp)
        1. [GET](#get)
            1. [Devices](#get-devices)
            2. [Queries](#get-queries)
        2. [SET](#SET)
            1. [Queries](#set-queries)
    2. [Accounts](#accounts)
        1. [Authentication](#authentication)
        2. [Preferences](#preferences)
3. [Code](#code)
    1. [pysattuner.py](#pysattuner-py)
    2. [devicemanager.py](#devicemanager-py)
    3. [configloader.py](#configloader-py)
    4. [snmpquery.py](#snmpquery-py)

# `Overview`

Pysattuner aims to be a simple JSON API built around the eve web application 
framework and pysnmp in order to provide JSON interfaces to broadcast television
devices that only have SNMP interfaces.

Pysattuner uses hooks to pull information from HTTP GET and PATCH requests for
SNMP calls defined in a config-file structure on a per-device basis. It then
takes this information to inform the hooks that perform SNMP queries to modify
the structure of the requests and use them to update a database that provides
the actual data storage for API calls.

Pysattuner provides full query hierarchy information and concurrency control as
part of the HTTP query process. Authentication control, while not yet
implemented, will also be part of the query system itself. This results in a
simple, straightforward query process. For example, presuming you have an
instance of the application hosted on your local machine serveing at port 5000,
an HTTP GET request to...

    http://127.0.0.1:5000/devices

If properly credentialed will prompt a response with all available devices and
their respective queries. This information is cleaned and reinitialized on each
start of the server, as its persistence is guaranteed by the config files.

# `API`

The API is composed of 2 parts: SNMP data and Account data.

## `SNMP`

SNMP data can be accessed over the API using HTTP GET and HTTP PATCH requests,
which mirror SNMP GET and SNMP SET requests, respectively.

### `GET`

HTTP Get queries can access SNMP data from the /devices and /queries resources

#### `GET Devices`

A raw query against the /devices resource, for example...

    http://127.0.0.1:5000/devices

will provice a JSON object containing all of the devices a user has access to.

A query agains a specific device name, for example...

    http://127.0.0.1:5000/devices/t1260

(if the device name is t1260) will provide information pertaining to that item
specifically. Each device is recorded as a specific item within the Devices
collection.

#### `GET Queries`

A raw query against the /queries resource, for example...

    http://127.0.0.1:5000/queries

will provice a JSON object containing all of the queries a user has access to.

A query agains a specific device name, for example...

    http://127.0.0.1:5000/queries/t1260_service_health

(if the query name is `t1260_service_health`) will provide information 
pertaining to that item specifically. Each query is recorded as a specific 
item within the Queries collection.

It's worth noting that as part of the startup initialization of these
collections, that every query gets a name in the convention...

    <device>_<query_name>

Query items will also contain an `_etag` item that is the essential
concurrency control value for submitting a PATCH query.

A HTTP GET against a query item does not retrieve the actual value from the
device unless the value in the database is more than 2 seconds old. If the
value in the database is less than two seconds old, the GET query gets the
database value.

Note that the GET query will update the `value` field if the value
is more than 2 seconds old but will not update `_etag` field. This is to
avoid breaking incoming patch requests simply because users are monitoring
SNMP values.

### `SET`

HTTP PATCH queries can modify the data in the /queries resource, which provokes
(via hooks) and SNMP SET against the device in question.

#### `SET Queries`

<!-- TODO Finish -->

With when attempting to alter setttings on devices, you obviously only want
to make queries against specific items within a resource. For example, if you
wanted to change the value of query "symbol_rate" for device"t1290", you would
send a HTTP PATCH to

    http://127.0.0.1:5000/queries/t1260_service_health

## `Accounts`

This section will contain information on the /accounts resource

### `Authentication`

This section will contain information on how Authentication information is
stored in the accounts resource.

### `Preferences`

This section will contain information on how Preference and preset information
is stored in the accounts resource.

# `Code`

## `pysattuner.py`
The core module that contains the webapp and hook logic.

pysattuner.py defines three functional resource endpoints: accounts, devices,
and queries. Accounts provides user account information. Devices provides
listings of available devices and the SNMP calls that they have available, as
well as certain ancilliary information such as a human-readable device name.
Queries provides information on the status of each individual SNMP call.

## `devicemanager.py`
A devicemanager class that simplifies access to the configured devices and their
calls through a single interface.

## `configloader.py`
A config file parser that loads configuration files for every SNMP device in a
given directory.

## `snmpquery.py`
A thin wrapper around pysnmp that radically simplifies the GETting and SETting
of SNMP values by allowing you to instantiate snmptarget() objects and make 
`getbyoid()` and `setbyoid()` calls against them.

