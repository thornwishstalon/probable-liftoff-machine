import uos
import ujson


class Config:
    CRED_FILE = "./config.creds"

    def __init__(self, id,  ssid=None, password=None, mqtt_broker=None, broker_password=None):
        self.ssid = ssid
        self.password = password
        self.mqtt_broker = mqtt_broker
        self.broker_password = broker_password
        self.mqtt_id = id

    def load(self):
        try:
            with open(self.CRED_FILE, "rb") as f:
                config = ujson.loads(f.read())
                if 'ssid' in config:
                    self.ssid = config['ssid']
                if 'password' in config:
                    self.password = config['password']
                if 'mqtt_broker' in config:
                    self.mqtt_broker = config['mqtt_broker']
                if 'broker_password' in config:
                    self.broker_password = config['broker_password']

            print("Loaded config from {:s}".format(self.CRED_FILE))

        except OSError:
            pass

        return self

    def remove(self):
        """
        1. Delete credentials file from disk.
        2. Set ssid and password to None
        """
        # print("Attempting to remove {}".format(self.CRED_FILE))
        pass
        try:
            uos.remove(self.CRED_FILE)
        except OSError:
            pass

        self.ssid = self.password = None

    def has_wifi(self):
        # Ensure credentials are not None or empty
        return all((self.ssid, self.password))
