import uasyncio
import ujson

import externallib.async_urequests as urequests
from common.event import LiftOffEvent
from module.subscriber import SubscriberList


class RemoteSubscriberCallback:
    def __init__(self, callbackUrl, _token=None):
        self.callbackUrl = callbackUrl
        self._token = _token

    def notify(self, event: LiftOffEvent):
        url = self.callbackUrl
        headers = {'Connection': 'Close'}
        if self._token:
            headers['Authorization'] = 'Bearer {}'.format(self._token)
        response_ref = urequests.post(url=url, headers=headers, data=ujson.dumps(event.to_json))
        if response_ref.status_code == 200:
            return response_ref.json()


class RemoteSubscriberList:

    def __init__(self, priority=100):
        self.subscriber_list = {}
        # remote priority
        self.priority = priority

    def register(self, event_tag: str, callback: RemoteSubscriberCallback, priority=100):
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

    def notify(self, data):
        print(data)
        event_tag = data['event_name']
        if event_tag in self.subscriber_list.keys():
            sorted_subs = sorted(self.subscriber_list[event_tag], key=lambda kv: kv.get('priority', 100))
            messages = []

            for sub in sorted_subs:
                task = uasyncio.create_task(sub["callback"].notify(data=data))
                messages.append(await task)

            return messages


class EventBus:
    def __init__(self):
        self._subscriber_list = SubscriberList()
        self.remote_subscriber_list = RemoteSubscriberList()

    def register_local_callback(self, event_tag, callback):
        self._subscriber_list.register(event_tag=event_tag, callback=callback)

    def register_remote_callback(self, event_tag, callback):
        self.remote_subscriber_list.register(event_tag=event_tag, callback=callback)

    def trigger_event(self, event_tag, event):
        event_data = {'event_name': event_tag, 'event': event}
        event_data = self._subscriber_list.notify(event_data)
        self.remote_subscriber_list.notify(event_data)
