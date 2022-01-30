import picoweb
import ujson

from bridge.trip import Trip
from common.event import EventFactory, EVENT_UPDATE_NEXT_QUEUE


class ParametersMissingException(Exception):
    pass


def _parse_query_string(qs):
    parameters = {}
    if qs:
        ampersand_split = qs.split("&")
        for element in ampersand_split:
            equal_split = element.split("=")
            parameters[equal_split[0]] = equal_split[1]

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
            headers = {"Access-Control-Allow-Origin": "*", 'Access-Control-Allow-Methods': "PUT, GET, OPTIONS",
                       'Access-Control-Allow-Headers': "Origin, Content-Type, Accept, Access-Control-Allow-Headers"}

            encoded = ujson.dumps(bridge.data_state.json)
            yield from picoweb.start_response(resp, content_type="application/json", headers=headers)
            yield from resp.awrite(encoded)
        else:
            yield from picoweb.http_error(resp, "405")

    @app.route("/floor")
    def floor(req, resp):
        headers = {"Access-Control-Allow-Origin": "*", 'Access-Control-Allow-Methods': "PUT, GET, OPTIONS",
                   'Access-Control-Allow-Headers': "Origin, Content-type, Accept, Access-Control-Allow-Headers"}

        if req.method == "GET":

            encoded = ujson.dumps({'current_floor': bridge.data_state.current_floor})

            yield from picoweb.start_response(resp, content_type="application/json", headers=headers)
            yield from resp.awrite(encoded)
        elif req.method == "OPTIONS":
            yield from picoweb.start_response(resp, headers=headers)

        elif req.method == "PUT":
            try:
                parameters = _parse_query_string(req.qs)
                _require_parameters(parameters, ["next"])
                bridge.schedule.schedule_trip(Trip(int(parameters["next"])))

                encoded = ujson.dumps("ok")
                yield from picoweb.start_response(resp, content_type="application/json", headers=headers)
                yield from resp.awrite(encoded)
                # trigger event
                bridge.mqtt.publish(
                    EVENT_UPDATE_NEXT_QUEUE,
                    EventFactory.create_event(
                        bridge.config.mqtt_id,
                        None,
                        bridge.data_state.next_queue
                    )
                )

            except ParametersMissingException:
                yield from picoweb.http_error(resp, "400")
        else:
            yield from picoweb.http_error(resp, "405")

    return app
