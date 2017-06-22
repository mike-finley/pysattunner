"""A simple device config file loader for pysattuner.py."""
import configparser
import os
import glob
import sys


class DeviceConfig(object):

    """
    Device configuration reader.

    Intended for the devices that are going to have SNMP configurations
    read for use by pysattuner.py.

    """

    def __init__(self, config_file):
        """Read config_file and parses into self.configuration."""
        self.filename = config_file
        self.configuration = configparser.ConfigParser()
        self.configuration.read(self.filename)

    def __str__(self):
        """Return filename of DeviceConfig instance, less extension.

        :returns: str

        """
        return os.path.basename(self.filename).rstrip(".conf")

    def get_sections(self):
        """Return all sections of the ConfigParser() object.

        :returns: list of sections

        """
        return self.configuration.sections()

    def get_keys(self, config_section):
        """Return all keys in a section of self.configuration.

        :config_section: str section from config file
        :returns: @todo

        """
        output = []
        for config_key in self.configuration[config_section]:
            output.append(config_key)
        return output

    def get_value(self, config_section, config_key):
        """Get the value for a key in a section inside self.configuraton.

        :config_section: str of section in self.configuration
        :config_key: str of key in self.configuration
        :returns: str

        """
        return self.configuration[config_section][config_key]


class ConfigBundle(object):

    """A bundle of DeviceConfig() objects."""

    def __init__(self, directory):
        """Load files ending in .conf from given directory.

        :directory: a str of a directory without trailing slash

        """
        self.directory = directory
        self.contents = []
        for config_file in glob.glob("/".join([os.getcwd(),
                                               self.directory,
                                               "*.conf"])):
            self.contents.append(DeviceConfig(config_file))

    def full_breakdown(self):
        """Pretty print the contents of the ConfigBundle().

        :returns: a multiline str, possibly very large.

        """
        output = ["Performing load_dir test...",
                  "".join(["Directory ",
                           str(self.directory),
                           " contains...:"]),
                  str([str(config) for config in self.contents]),
                  "Configurations:"]
        for config in self.contents:
            output.append(str(config))
            output.append(str(config.get_sections()))
            for section in config.get_sections():
                output.append("".join([section, ":"]))
                for key in config.get_keys(section):
                    output.append(
                        ":".join([key, config.get_value(section, key)])
                        )
        output.append("Done loading configs.")
        return "\n".join(output)

    def get_contents(self):
        """Return contents of the ConfigBundle object.

        :returns: list of DeviceConfig() objects.

        """
        return self.contents

if __name__ == '__main__':
    if len(sys.argv) == 2:
        CONFIG = ConfigBundle(sys.argv[1])
        print(CONFIG.full_breakdown())
    else:
        print("""Incorrect number of arguments.
Please enter a subdir of the current directory.""")
