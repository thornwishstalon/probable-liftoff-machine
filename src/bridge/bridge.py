import picoweb

from bridge.subscriber import EventBus, RemoteSubscriberCallback


class Bridge:
    def __init__(self):
        pass


def setup_bridge() -> picoweb.WebApp:
    app = picoweb.WebApp(__name__)
    bus = EventBus()

    @app.route("/register")
    def register(req, resp):
        if req.method == "POST":
            yield from req.read_form_data()
        else:
            yield from picoweb.http_error(resp, "405")

        bus.remote_subscriber_list(req.form['event_name'], RemoteSubscriberCallback(req.form['callback']))

        yield from picoweb.start_response(resp)
        yield from resp.awrite("ok")

    @app.route("/notify")
    def notify(req, resp):
        if req.method == "POST":
            yield from req.read_form_data()
        else:
            yield from picoweb.http_error(resp, "405")

        bus.trigger_event(req.form['event_name'], RemoteSubscriberCallback(req.form['event']))
        yield from picoweb.start_response(resp)
        yield from resp.awrite("ok")

    return app
