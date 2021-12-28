class SubscriberCallback:
    def __init__(self, callback):
        self.callback = callback

    def notify(self, params):
        return self.callback(params)


class SubscriberList:

    def __init__(self):
        self.subscriber_list = {}
        self.priority = 100

    def register(self, event_tag, callback, priority=100):
        if not self.subscriber_list[event_tag]:
            self.subscriber_list[event_tag] = []

        self.subscriber_list[event_tag].append(
            {"priority": priority, "callback": SubscriberCallback(callback)}
        )

    def notify(self, params):
        event_tag = params['event_name']
        if self.subscriber_list[event_tag]:
            sorted_subs = sorted(self.subscriber_list[event_tag].items(), key=lambda kv: kv['priority'])
            message = []
            for sub in sorted_subs:
                message.append(sub.notify(params=params))

            return message
