import ujson

EVENT_PRE_TRIP_START = b"liftoff/trip/start/pre"
EVENT_TRIP_START = b"liftoff/trip/start"
EVENT_POST_TRIP_START = b"liftoff/trip/start/post"
EVENT_TRIP_READY = b"liftoff/trip/ready"
EVENT_PRE_TRIP_END = b"liftoff/trip/end/pre"
EVENT_TRIP_END = b"liftoff/trip/end/post"
EVENT_POST_TRIP_END = b"liftoff/post/trip/end"
#
EVENT_UPDATE_FLOOR = b"liftoff/update/floor"
EVENT_MOVEMENT_UPDATE = b"liftoff/move/to"
EVENT_POWER_UPDATE = b"liftoff/power"
EVENT_POWER_TRACK_DONE = b"liftoff/power/tracked"


class EventPayload:
    def __init__(self, transaction_code, payload):
        self.code = transaction_code
        self.payload = payload

    @property
    def json(self):
        """returns json string"""
        data = {}
        if self.code:
            data["id"] = self.code
        for key, value in self.payload.items():
            data[key] = value
        return ujson.dumps(data)


class EventFactory:

    @classmethod
    def create_event(cls, source_id, transaction_code, payload):
        payload['source'] = source_id
        return EventPayload(transaction_code, payload)


