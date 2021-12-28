from module.liftoff_module import LiftoffModule
from module.subscriber import SubscriberList
from module.event import EVENT_TRIP_READY, EVENT_POST_TRIP_START, EVENT_PRE_TRIP_END, EVENT_TRIP_END, \
    EVENT_POST_TRIP_END


class MovementModule(LiftoffModule):

    def __init__(self, essid=None):
        super().__init__(essid)
        self.current_floor = 0

    @property
    def routes(self):
        return {b"/floor", self.floor}

    def floor(self):
        return {'current_floor': self.current_floor}

    @property
    def subscriber(self):
        subs = SubscriberList()
        subs.register(EVENT_TRIP_READY, self.move)
        return subs

    @property
    def part_of(self):
        # todo
        return []

    def move(self, params):
        """do the 'moving'"""
        # todo: add code and trigger other events accordingly e.g.
        self.trigger_event(EVENT_POST_TRIP_START, {})
        self.trigger_event(EVENT_PRE_TRIP_END, {})
        self.trigger_event(EVENT_TRIP_END, {})
        self.trigger_event(EVENT_POST_TRIP_END, {})
        pass


module = MovementModule()
module.start()
