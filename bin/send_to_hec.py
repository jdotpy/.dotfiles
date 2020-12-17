#!/usr/bin/env python3
import threading
import argparse
import requests
import time
import queue
import json
import sys
import os

class HEC():
    BATCH_SIZE = 50

    def __init__(self, hosts, user=None, password=None, token=None, workers=20, index=None, source=None, sourcetype=None, host=None):
        self.hosts = hosts
        self.user = user
        self.password = password
        if token:
            self.client = token
        else:
            self.client = uuid.uuid4()
        self.queue = queue.Queue(maxsize=workers)
        self.host_lock = threading.Lock()
        self.done = False

        # Default attributes
        self.index = index
        self.source = source
        self.sourcetype = sourcetype
        self.host = host

        self.sessions = {host: requests.Session() for host in hosts}
        if token:
            for session in self.sessions.values():
                session.headers['Authorization'] = 'Splunk {}'.format(token)
        self._workers = []

        self.worker_count = workers
        self.next_host = self._session_iter()

        self._event_count = 0
        self._batch_count = 0

    def wrap_event(self, event, host=None, timestamp=None, index=None, source=None, sourcetype=None):
        return {
            'time': timestamp or time.time(),
            'host': host or 'localhost',
            'index': index or self.index,
            'source': source or self.source,
            'sourcetype': sourcetype or self.sourcetype,
            'event': event,
        }

    def _session_iter(self):
        host_list = list(self.sessions.items())
        while True:
            for host, session in host_list:
                yield (host, session)

    def create_endpoint(self):
        hosts = self.sessions.keys()
        for host in hosts:
            session = self.sessions[host]
            response = requests.post(
                'https://{}:8089/services/data/inputs/http?output_mode=json'.format(host),
                auth=(self.user, self.password),
                data={'name': self.client},
                verify=False,
            )
            if not response.ok:
                self.sessions.pop(host)
                print(response.text)
            else:
                result = response.json()
                token = result['entry'][0]['content']['token']
                session.headers['Authorization'] = 'Splunk {}'.format(token)

    def _send_batch(self, events):
        with self.host_lock:
            host, session = next(self.next_host)
        self._event_count += len(events)
        self._batch_count += 1 
        data = '\n'.join([json.dumps(event) for event in events])
        response = session.post(
            'https://{}:8088/services/collector/event'.format(host),
            data=data,
            verify=False,
        )
        response_content = response.text
        if not response.ok:
            print('Failing HEC ingest on host {}:\n{}'.format(host, response_content))
            with self.host_lock:
                self.sessions.pop(host)
                if len(self.sessions) == 0:
                    raise ValueError('All sessions failed on HEC')
                self.next_host = self._session_iter()

            self._send_batch(events)

    def start(self):
        def _worker():
            while True:
                try:
                    events = self.queue.get(block=True, timeout=1)
                except queue.Empty:
                    if self.done:
                        break
                    else:
                        continue
                batches = 0
                while len(events) > 0:
                    batch = events[:self.BATCH_SIZE]
                    events = events[self.BATCH_SIZE:]
                    self._send_batch(batch)
                    batches += 1
                self.queue.task_done()

        for i in range(self.worker_count):
            thread = threading.Thread(target=_worker)
            self._workers.append(thread)
            thread.start()

    def send(self, events):
        self.queue.put(events)

    def finish(self):
        self.queue.join()
        self.done = True
        for worker in self._workers:
            worker.join()


def send_data(targets, index=None, source=None, sourcetype=None, host=None, data=None, token=None):
    client = HEC(targets, token=token, index=index, source=source, sourcetype=sourcetype)
    client.start()
    closable = True
    if data == '-':
        source = sys.stdin
        closable = False
    else:
        source = open(data, 'r')

    batch = []
    try:
        for line in source:
            batch.append(client.wrap_event(line))
            if len(batch) > HEC.BATCH_SIZE:
                client.send(batch)
                batch = []
        if batch:
            client.send(batch)
    finally:
        client.finish()


def cli():
    default_token = os.environ.get('HECLOADER_TOKEN', None)
    parser = argparse.ArgumentParser(prog='Send things to HEC! (Splunk HTTP Event Collector)')
    parser.add_argument('targets', nargs='+', help='Splunk indexers to use')
    parser.add_argument('-i', '--index', help='Splunk index to use', default=os.environ.get('HECLOADER_INDEX', 'main'))
    parser.add_argument('-s', '--source', help='source to assign', default=os.environ.get('HECLOADER_SOURCE', 'hecloader'))
    parser.add_argument('-y', '--sourcetype', help='sourcetype to assign', default=os.environ.get('HECLOADER_SOURCETYPE', 'hecloader'))
    parser.add_argument('-o', '--host', help='host to assign to logs (not splunk host)', default=os.environ.get('HECLOADER_HOST', 'localhost'))
    parser.add_argument('-d', '--data', help='data to load ("-" for stdin)', default='-')
    parser.add_argument('-t', '--token', help='HEC token to use', required=not default_token, default=default_token)

    args = parser.parse_args()
    params = args.__dict__
    targets = params.pop('targets')
    send_data(targets, **params)

if __name__ == '__main__':
    cli()
