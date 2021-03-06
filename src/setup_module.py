wlan = None


def setup_stuff(ssid: str, password: str):
    import network
    def kill_connection():
        global wlan
        if wlan.isconnected():
            wlan.disconnect()
            wlan = None

    def do_connect():
        global wlan
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())

    do_connect()

    import upip
    upip.install('micropython-abc')
    upip.install('micropython-umqtt.simple')

    kill_connection()


setup_stuff('<ssid>', '<pw>')
