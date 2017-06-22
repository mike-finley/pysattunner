"""Simple SNMP query module for pysattuner.py."""
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902


class SNMPTarget(object):

    """Target for SNMP queries with built-in query methods."""

    def __init__(self, host, version=1, port=161):
        """Initialize SNMPTarget object for given host."""
        self.host = host
        self.snmpver = int(version)
        self.snmpport = int(port)

    def get_by_oid(self, oid, community='public',
                   snmpv3cred=('authkey1', 'privkey1')):
        """Return the results of an SNMP GET."""
        # TODO fix the test-agent and test-user usage here
        if self.snmpver == 1:
            authdata = cmdgen.CommunityData('test-agent', community, 0)
        elif self.snmpver == 2:
            authdata = cmdgen.CommunityData('test-agent', community)
        elif self.snmpver == 3:
            authdata = cmdgen.UsmUserData('test-user', snmpv3cred[0],
                                          snmpv3cred[1])

        errorindication, errorstatus, errorindex, varbinds = \
            cmdgen.CommandGenerator().getCmd(
                authdata, cmdgen.UdpTransportTarget((
                    self.host, self.snmpport)), oid
                )

        if errorindication:
            return str(errorindication)
        else:
            if errorstatus:
                return varbinds[0][1].prettyPrint()
            else:
                return varbinds[0][1].prettyPrint()

    def set_by_oid(self, oid, value, community='private',
                   snmpv3cred=('authkey1', 'privkey1')):
        """Return the results of an SNMP SET."""
        # TODO fix the test-agent and test-user usage here
        if self.snmpver == 1:
            authdata = cmdgen.CommunityData('test-agent', community, 0)
        elif self.snmpver == 2:
            authdata = cmdgen.CommunityData('test-agent', community)
        elif self.snmpver == 3:
            authdata = cmdgen.UsmUserData(
                'test-user', snmpv3cred[0], snmpv3cred[1]
            )

        if isinstance(value, int):
            errorindication, errorstatus, errorindex, varbinds = \
                cmdgen.CommandGenerator().setCmd(
                    authdata, cmdgen.UdpTransportTarget(
                        (self.host, self.snmpport)),
                    (oid, rfc1902.Integer(value))
                )

        if errorindication:
            return str(errorindication)
        else:
            if errorstatus:
                return varbinds[0][1].prettyPrint()
            else:
                return varbinds[0][1].prettyPrint()
