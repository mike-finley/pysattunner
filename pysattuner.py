"""Pysattuner.py core."""
from eve import Eve, utils
import json
from datetime import datetime, timedelta
import pytz
from configloader import ConfigBundle
from devicemanager import DeviceManager

# Temporal distance between two successive SNMP GET
# requests. This is to prevent over-saturation when
# recent data is stored in the DB. Your mileage may
# vary depending on your use case.

GET_DELTA = timedelta(seconds=2)

# GMT instance for use in delta checing
GMT = pytz.timezone('GMT')


def flatten(unflat, ltypes=(list, tuple)):
    """Pilfered function, flattens iterables."""
    ltype = type(unflat)
    unflat = list(unflat)
    i = 0
    while i < len(unflat):
        while isinstance(unflat[i], ltypes):
            if not unflat[i]:
                unflat.pop(i)
                i -= 1
                break
            else:
                unflat[i:i + 1] = unflat[i]
        i += 1
    return ltype(unflat)


def query_get_callback(request, lookup):  # pylint: disable=unused-argument
    """Run SNMP GET as necessary.

    Does an SNMP GET if the database record is stale.

    :response: flask.request object
    :returns: None

    """
    if lookup:
        gmt_now = datetime.now(GMT).replace(microsecond=0)
        device = lookup['name'].split('_', 1)[0]
        query = lookup['name'].split('_', 1)[1]
        status = pysattuner.data.driver.db['queries'].find_one(
            {'name': lookup['name']})
        if status['_updated'] + GET_DELTA < gmt_now:  # pylint: disable=no-value-for-parameter
            status['value'] = devices.snmp_get(device, query)
            status['_updated'] = gmt_now
            pysattuner.data.driver.db['queries'].update(
                {'_id': status['_id']}, status)


def query_patch_callback(request, lookup):
    """Run SNMP SET as necessary.

    :lookup: current lookup dictionary
    :request: flask.request object
    :returns: none

    """
    # TODO right now this runs regardless of whether etag matches. Big problem
    if lookup:
        device = lookup['name'].split('_', 1)[0]
        query = lookup['name'].split('_', 1)[1]
        if devices.snmp_set(device,
                            query,
                            int(request.get_json()['value']
                            )) != request.get_json()['value']:  # pylint: disable=bad-continuation
            request = None

def spawn_device_resources(devicemanager, eveapp):
    """Instantiate all of the devices in the Eve app.

    Give a DeviceManager instance and an Eve instance,
    this function will loop through all of the devices
    and create resource endpoints for them within the
    app.

    :devicemanager: a DeviceManager instance
    :pysattuner: an Eve instance
    :returns: None

    """
    # First we programatically create the schema for /devices
    eveapp.register_resource('devices', {
        'schema': {
            'name': {
                'allowed': [device for device in devicemanager.get_devices()],
                'type': 'string',
                'unique': True,
                'required': True},
            'queries': {
                'type': 'list',
                'allowed': flatten(
                    [["_".join([device, query])
                      for query in devicemanager.get_queries(device)]
                     for device in devicemanager.get_devices()])}},
        'item_lookup_field': 'name',
        'item_url': 'regex("[\\w]+")',
        'item_title': 'device',
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'DELETE']})
    # Now we create the schema for /queries
    eveapp.register_resource('queries', {
        'schema': {
            'name': {
                'type': 'string',
                'allowed': flatten(
                    [["_".join([device, query])
                      for query in devicemanager.get_queries(device)]
                     for device in devicemanager.get_devices()]),
                'unique': True,
                'required': True},
            'device': {'type': 'string'},
            'value': {'type': 'number'}},
        'item_lookup_field': 'name',
        'item_url': 'regex("[\\w]+")',
        'item_title': 'query',
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'DELETE']})
    # Add hooks for SNMP GET and SET
    eveapp.on_pre_GET_queries += query_get_callback
    eveapp.on_pre_PATCH_queries += query_patch_callback
    # Now we do a population of the device and query collections.
    # We use the build in test_client method in order to make
    # sure that all of the metadata gets inserted along with.
    eveapp.test_client().delete('/devices')
    eveapp.test_client().delete('/queries')
    for device in devicemanager.get_devices():
        eveapp.test_client().post(
            '/devices',
            data=json.dumps({
                'name': device,
                'queries': ["_".join([device, query])
                            for query in devicemanager.get_queries(device)]}),
            content_type='application/json')
        for query in devicemanager.get_queries(device):
            eveapp.test_client().post(
                '/queries',
                data=json.dumps({
                    'name': "_".join([device, query]),
                    'device': device,
                    'value': 0}),
                content_type='application/json')


devices = DeviceManager(ConfigBundle("conf"))  # pylint: disable=invalid-name
pysattuner = Eve(settings='dev_settings.py')  # pylint: disable=invalid-name
spawn_device_resources(devices, pysattuner)

if __name__ == '__main__':
    pysattuner.run(host='0.0.0.0', port=5000, debug=True)
