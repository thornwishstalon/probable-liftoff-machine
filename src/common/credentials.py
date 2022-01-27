import uos
import ujson


class Config:
    CRED_FILE = "./config.creds"

    def __init__(self, mqtt_id, ssid=None, password=None, mqtt_broker=None, broker_password=None):
        self.ssid = ssid
        self.password = password
        self.mqtt_broker = mqtt_broker
        self.broker_password = broker_password
        self.mqtt_id = mqtt_id

        print(self.mqtt_id)

    def load(self):
        try:
            with open(self.CRED_FILE, "rb") as f:
                config = ujson.loads(f.read())
                print(config.keys())

                if "ssid" in config.keys():
                    self.ssid = config["ssid"]
                    print(self.ssid)
                if "password" in config.keys():
                    self.password = config["password"]
                    print(self.password)
                if "mqtt_broker" in config.keys():
                    self.mqtt_broker = config["mqtt_broker"]
                    print(self.mqtt_broker)
                if "broker_password" in config.keys():
                    self.broker_password = config["broker_password"]
                    print(self.broker_password)

            print("Loaded config from {:s}".format(self.CRED_FILE))

        except OSError as e:
            print(e)
        return self

    def remove(self):
        """
        1. Delete credentials file from disk.
        2. Set ssid and password to None
        """
        print("Attempting to remove {}".format(self.CRED_FILE))
        self.ssid = self.password = None

    def has_wifi(self):
        # Ensure credentials are not None or empty
        return self.ssid is not None
