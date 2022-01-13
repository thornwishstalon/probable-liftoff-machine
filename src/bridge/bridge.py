import picoweb
import ujson

from bridge.bridge_server import BridgeServer


def setup_bridge(bridge:BridgeServer) -> picoweb.WebApp:
    app = picoweb.WebApp(__name__)

    @app.route("/floor")
    def register(req, resp):
        if req.method == "GET":
            encoded = ujson.dumps({'current_floor': bridge.state.current_floor})

            yield from picoweb.start_response(resp, content_type="application/json")
            yield from resp.awrite(encoded)
        else:
            yield from picoweb.http_error(resp, "405")

        yield from picoweb.start_response(resp)
        yield from resp.awrite("ok")

    return app
