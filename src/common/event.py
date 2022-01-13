from abc import abstractmethod

EVENT_PRE_TRIP_START = "liftoff.pre.trip.start"
EVENT_TRIP_START = "liftoff.trip.start"
EVENT_POST_TRIP_START = "liftoff.post.trip.start"
EVENT_TRIP_READY = "liftoff.trip.ready"
EVENT_PRE_TRIP_END = "liftoff.pre.trip.end"
EVENT_TRIP_END = "liftoff.post.trip.end"
EVENT_POST_TRIP_END = "liftoff.post.trip.end"
#
EVENT_UPDATE_FLOOR = "liftoff.update.floor"


class LiftOffEvent:
    def __init__(self, event_tag:str, data):
        self._event_tag = event_tag
        self._data = data

    @abstractmethod
    @property
    def to_json(self):
        pass

