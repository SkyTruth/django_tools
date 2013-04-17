import subprocess
import json
import threading
import tempfile
import contextlib
import ais

def convert(f):
    print "Converting"
    buffer = ''
    for line in f:
        if line.startswith("\\"):
            line = line[1:]
            header, nmea = line.split("\\", 1)
            header = dict(item.upper().split(":") for item in header.split("*")[0].split(","))
        else:
            nmea = line
            header = {}

        buffer += nmea.split(',')[5]
        pad = int(nmea.split('*')[0][-1])

        try:
            msg = ais.decode(buffer, pad)
        except:
            pass
        else:
            buffer = ''
            msg.update(header)
            yield msg
