import picoweb
import ujson

from bridge.trip import Trip


class ParametersMissingException(Exception):
    pass


def _parse_query_string(qs):
    parameters = {}
    if qs:
        ampersandSplit = qs.split("&")
        for element in ampersandSplit:
            equalSplit = element.split("=")
            parameters[equalSplit[0]] = equalSplit[1]

    return parameters


def _require_parameters(elements, required):
    for r in required:
        if r not in elements.keys():
            raise ParametersMissingException()


def setup_bridge(bridge) -> picoweb.WebApp:
    app = picoweb.WebApp(__name__)
    
    @app.route("/state")
    def state(req, resp):
        if req.method == "GET":
            headers = {"Access-Control-Allow-Origin": "*"}
            headers['Access-Control-Allow-Methods'] = "PUT, GET, OPTIONS"
            headers['Access-Control-Allow-Headers'] = "Origin, Content-Type, Accept, Access-Control-Allow-Headers"
            
            encoded = ujson.dumps( bridge.data_state.json )
            yield from picoweb.start_response(resp, content_type="application/json",headers=headers)
            yield from resp.awrite(encoded)
        else:
            yield from picoweb.http_error(resp, "405")

    @app.route("/floor")
    def floor(req, resp):
        headers = {"Access-Control-Allow-Origin": "*" }
        headers['Access-Control-Allow-Methods'] = "PUT, GET, OPTIONS"
        headers['Access-Control-Allow-Headers'] = "Origin, Content-type, Accept, Access-Control-Allow-Headers"
        
        if req.method == "GET":

            encoded = ujson.dumps({'current_floor': bridge.data_state.current_floor})

            yield from picoweb.start_response(resp, content_type="application/json",headers=headers)
            yield from resp.awrite(encoded)
        elif req.method == "OPTIONS":           
            yield from picoweb.start_response(resp, headers=headers)

        elif req.method == "PUT":
            try:
                parameters = _parse_query_string(req.qs)
                _require_parameters(parameters, ["next"])
                next = (int)(parameters["next"])
                bridge.schedule.schedule_trip(Trip(next))

                encoded = ujson.dumps("ok")
                yield from picoweb.start_response(resp, content_type="application/json", headers=headers)
                yield from resp.awrite(encoded)

            except ParametersMissingException:
                yield from picoweb.http_error(resp, "400")
        else:
            yield from picoweb.http_error(resp, "405")

    return app


