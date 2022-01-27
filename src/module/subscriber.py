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
            {"priority": priority, "callback": callback}
        )

    def notify(self, topic, message):
        if topic in self.subscriber_list.keys():
            sorted_subs = sorted(self.subscriber_list[topic], key=lambda kv: kv.get('priority', 100))
            messages = []
            for sub in sorted_subs:
                print(sub)
                resp = sub['callback'](message)
                messages.append(resp)
            print(messages)
            return messages
