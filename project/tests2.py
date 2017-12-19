## NOTE. THIS WAS INSPIRED BY PIAZZA #367

import time
import json
import unicodedata
import datetime
import uuid
import asyncio
import unittest
import os
import subprocess

### CHANGE THESE PORT NUMBERS!!!
SERVER_PORT_MAP = {'Alford': 8610,
                   'Ball': 8611,
                   'Hamilton': 8612,
                   'Holiday': 8613,
                   'Welsh': 8614,
                   }


async def communicate_with(server_name, command):
    loop = asyncio.get_event_loop()
    reader, writer = await asyncio.open_connection('127.0.0.1', SERVER_PORT_MAP[server_name],
                                                   loop=loop)
    writer.write(command)
    await writer.drain()
    data = await reader.read()
    writer.close()
    return data


def do_communicate(server_name, command):
    loop = asyncio.get_event_loop()
    r = loop.run_until_complete(communicate_with(server_name, command))
    return r


class ServerHerdTest(unittest.TestCase):
    def setUp(self):
        for _, port in SERVER_PORT_MAP.items():
            r = subprocess.run(['lsof', '-iTCP:' + str(port), '-sTCP:LISTEN'], stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, check=False)
            assert r.returncode == 0, "no process is listening on port %d; is the server running?" % port


    def test_duplicate_iamat_handling(self):
        client_id = "kiwi.ucla.edu"
        now = datetime.datetime.now().timestamp()
        nowstr = str(now)
        oldstr = str(now-1000)
        newstr = str(now+1000)
        first_at = do_communicate('Holiday',
                                  b'IAMAT %s +34.068930-118.445127 %b\n' % (client_id.encode(), nowstr.encode()))
        second_at = do_communicate('Holiday', b'IAMAT %s +34.068930-118.445127 %b\n' % (
            client_id.encode(), oldstr.encode()))
        self.assertEqual(second_at, first_at, "should ignore location update with earlier timestamp")
        third_at = do_communicate('Holiday', b'IAMAT %s +34.068930-118.445127 %b\n' % (
            client_id.encode(), newstr.encode()))
        self.assertNotEqual(third_at, first_at, "should accept location update with later timestamp")

    def test_basic_location_propagation(self):
        client_id = "kiwi.ucla.edu"
        now = time.time()
        my_time_stamp = "%.9f" % now
        first_at = do_communicate('Alford', b'IAMAT %s +34.068930-118.445127 %b\n' % (
            client_id.encode(), my_time_stamp.encode())).rstrip()
        time.sleep(0.5) # allow some time for location information to be propagated
        second_at = do_communicate('Ball', b'WHATSAT %s 1 1\n' % (client_id.encode())).split(b'\n')[0].rstrip()
        print("\nfirst: " + str(first_at))
        print("\nsecond: " + str(second_at))

       #  self.assertEqual(second_at, first_at, "Ball should answer WHATSAT queries using location info from Alford")
       #  third_at = do_communicate('Holiday', b'WHATSAT %s 1 1\n' % (client_id.encode())).split(b'\n')[0].rstrip()
       #  self.assertEqual(third_at, first_at, "Holiday should answer WHATSAT queries using location info from Alford")
       #  fourth_at = do_communicate('Hamilton', b'WHATSAT %s 1 1\n' % (client_id.encode())).split(b'\n')[0].rstrip()
       #  self.assertEqual(fourth_at, first_at, "Hamilton should answer WHATSAT queries using location info from Alford")
       #  fifth_at = do_communicate('Welsh', b'WHATSAT %s 1 1\n' % (client_id.encode())).split(b'\n')[0].rstrip()
       # # self.assertEqual(fifth_at, first_at, "Welsh should answer WHATSAT queries using location info from Alford")

def main():
    os.environ['TZ'] = 'UTC'
    print("Will start automated testing")
    unittest.main(verbosity=2, failfast=True)


if __name__ == '__main__':
    main()