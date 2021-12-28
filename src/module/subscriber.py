class SubscriberCallback:
    def __init__(self, callback):
        self.callback = callback

    def notify(self, params, data):
        return self.callback(params, data)


class SubscriberList:

    def __init__(self, priority=100):
        self.subscriber_list = {}
        # remote priority
        self.priority = priority

    def register(self, event_tag, callback, priority=100):
        """

        :param event_tag:
        :param callback:
        :param priority: local priority
        :return:
        """
        if event_tag not in self.subscriber_list.keys():
            self.subscriber_list[event_tag] = []

        self.subscriber_list[event_tag].append(
            {"priority": priority, "callback": SubscriberCallback(callback)}
        )

    def notify(self, params, data):
        print(params)
        print(data)
        event_tag = data['event_name']
        if event_tag in self.subscriber_list.keys():
            sorted_subs = sorted(self.subscriber_list[event_tag], key=lambda kv: kv.get('priority', 100))
            message = []
            for sub in sorted_subs:
                message.append(sub["callback"].notify(params=params, data=data))

            return message

