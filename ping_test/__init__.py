import sys
import time
from random import randint

import pythonping
from pythonping import network, executor
from pythonping.utils import random_text

SEED_IDs = []


class Communicator(executor.Communicator):
    def __init__(self, target, payload_provider, timeout, interval, socket_options=(), seed_id=None,
                 verbose=False, output=sys.stdout, source=None, repr_format=None):
        super().__init__(
            target, payload_provider, timeout, interval, socket_options, seed_id,
            verbose, output, source, repr_format)

    def run(self, match_payloads=False):
        """Performs all the pings and stores the responses

         :param match_payloads: optional to set to True to make sure requests and replies have equivalent payloads
         :type match_payloads: bool"""
        self.responses.clear()
        identifier = self.seed_id
        seq = 1
        for payload in self.provider:
            icmp_out = self.send_ping(identifier, seq, payload)
            if not match_payloads:
                _res = self.listen_for(identifier, self.timeout, None, icmp_out)
            else:
                _res = self.listen_for(identifier, self.timeout, icmp_out.payload, icmp_out)
            self.responses.append(_res)

            seq = self.increase_seq(seq)

            if self.interval:
                time.sleep(self.interval)
            yield _res


def ping_tester(target,
                timeout=2,
                count=4,
                size=1,
                interval=0,
                payload=None,
                sweep_start=None,
                sweep_end=None,
                df=False,
                verbose=False,
                out=sys.stdout,
                match=False,
                source=None,
                out_format='legacy'):
    provider = pythonping.payload_provider.Repeat(b'', 0)
    if sweep_start and sweep_end and sweep_end >= sweep_start:
        if not payload:
            payload = random_text(sweep_start)
        provider = pythonping.payload_provider.Sweep(payload, sweep_start, sweep_end)
    elif size and size > 0:
        if not payload:
            payload = random_text(size)
        provider = pythonping.payload_provider.Repeat(payload, count)
    options = ()
    if df:
        options = network.Socket.DONT_FRAGMENT

    # Fix to allow for pythonping multithreaded usage;
    # no need to protect this loop as no one will ever surpass 0xFFFF amount of threads
    while True:
        # seed_id needs to be less than or equal to 65535 (as original code was seed_id = getpid() & 0xFFFF)
        seed_id = randint(0x1, 0xFFFF)
        if seed_id not in SEED_IDs:
            SEED_IDs.append(seed_id)
            break

    try:
        comm = Communicator(target, provider, timeout, interval, socket_options=options, verbose=verbose,
                            output=out,
                            seed_id=seed_id, source=source, repr_format=out_format)

        for i in comm.run(match_payloads=match):
            yield i
    except Exception:
        raise
    finally:
        SEED_IDs.remove(seed_id)


