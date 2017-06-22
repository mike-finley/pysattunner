"""DeviceManager support classes for pysattuner."""

from snmpquery import SNMPTarget


class DeviceManagerTarget(object):

    """A single target device for DeviceManager core."""

    def __init__(self, config_object):
        """Create a single device from a config object."""
        self.conf = config_object
        self.snmp = SNMPTarget(self.conf.get_value("device_info", "host"),
                               self.conf.get_value("device_info", "snmp_ver"),
                               self.conf.get_value("device_info", "snmp_port"))

    def get_name(self):
        """Get the device name for the device.

        :returns: str

        """
        return self.conf.get_value("device_info", "name")

    def get_queries(self):
        """Get all possible SNMP queries for device.

        :returns: list of strings of query names

        """
        return [query for query in self.conf.get_keys("snmp_queries")]

    def snmp_get(self, query):
        """Perform an SNMP GET for given query.

        :query: str of query name
        :returns: str of output

        """
        if int(self.conf.get_value("device_info", "snmp_ver")) <= 2:
            return self.snmp.get_by_oid(
                self.conf.get_value("snmp_queries", query),
                community=self.conf.get_value("device_info",
                                              "snmp_public_community"))
        elif int(self.conf.get_value("device_info", "snmp_ver")) == 3:
            return self.snmp.get_by_oid(
                self.conf.get_value("snmp_queries", query),
                snmpv3cred=(
                    self.conf.get_value("device_info", "snmpv3_cred_authkey"),
                    self.conf.get_value("device_info", "snmpv3_cred_privkey")))

    def snmp_set(self, query, value):
        """Perform SNMP SET for given query and value.

        :query: str of query name
        :value: appropriate type for value to be set
        :returns: str

        """
        if int(self.conf.get_value("device_info", "snmp_ver")) <= 2:
            return self.snmp.set_by_oid(
                self.conf.get_value("snmp_queries", query),
                value,
                community=self.conf.get_value("device_info",
                                              "snmp_private_community"))
        elif int(self.conf.get_value("device_info", "snmp_ver")) == 3:
            return self.snmp.set_by_oid(
                self.conf.get_value("snmp_queries", query),
                value,
                snmpv3cred=(
                    self.conf.get_value("device_info", "snmpv3_cred_authkey"),
                    self.conf.get_value("device_info", "snmpv3_cred_privkey")))


class DeviceManager(object):

    """
    The primary handler class for SNMP devices.

    Use this class to manage a passel  of DeviceManagerTarget
    objects instead of creating a data structure inside pysattuner,
    which is already plenty full of actual webapp guts.
    """

    def __init__(self, config_bundle):
        """
        Create all of the devices.

        Spawns all of the DeviceManagerTarget objects from
        a ConfigBundle object, placing them into a dict
        keyed on their filenames.

        :config_bundle: a ConfigBundle object
        """
        self.contents = {}
        for config_object in config_bundle.get_contents():
            self.contents[str(config_object)] = \
                (DeviceManagerTarget(config_object))

    def __str__(self):
        """Pretty print devices in manager.

        :returns: str

        """
        print(", ".join([self.contents[device] for device in self.contents]))

    def add_device(self, config):
        """Add a new device to the DeviceManager core.

        Pass in a DeviceConfig object to add it to the dict.
        :arg1: @todo
        :returns: @todo

        """
        self.contents[str(config)] = config

    def get_devices(self):
        """Return a list of all DeviceManagerTarget object keys.

        :returns: list of keys in self.config

        """
        return [device for device in self.contents]

    def get_name(self, device):
        """Get the device name for the device.

        :device: str key of a DeviceManagerTarget from get_devices
        :returns: str

        """
        return self.contents[device].get_name()

    def get_queries(self, device):
        """Get all possible SNMP queries for device.

        :device: str key of a DeviceManagerTarget from get_devices
        :returns: list of strings of query names

        """
        return self.contents[device].get_queries()

    def snmp_get(self, device, query):
        """Perform an SNMP GET for given query.

        :device: str key of a DeviceManagerTarget from get_devices
        :query: str of query name
        :returns: str of output

        """
        return self.contents[device].snmp_get(query)

    def snmp_set(self, device, query, value):
        """Perform SNMP SET for given query and value.

        :device: str key of a DeviceManagerTarget from get_devices
        :query: str of query name
        :value: appropriate type for value to be set
        :returns: str

        """
        return self.contents[device].snmp_set(query, value)
