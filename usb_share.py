#!/usr/bin/python3

import time
import os
from watchdog.observers import Observer
from watchdog.events import *

CMD_MOUNT = "modprobe g_mass_storage file=/piusb.bin stall=0 ro=1"
CMD_UNMOUNT = "modprobe -r g_mass_storage"
CMD_SYNC = "sync"

WATCH_PATH = "/mnt/usb_share"
ACT_EVENTS = [DirDeletedEvent, DirMovedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent]
ACT_TIME_OUT = 5


class DirtyHandler(FileSystemEventHandler):
    def __init__(self):
        self.reset()

    def on_any_event(self, event):
        if type(event) in ACT_EVENTS:
            self._dirty = True
            self._dirty_time = time.time()

    @property
    def dirty(self):
        return self._dirty

    @property
    def dirty_time(self):
        return self._dirty_time

    def reset(self):
        self._dirty = False
        self._dirty_time = 0
        self._path = None


os.system(CMD_MOUNT)

evh = DirtyHandler()
observer = Observer()
observer.schedule(evh, path=WATCH_PATH, recursive=True)
observer.start()

try:
    while True:
        while evh.dirty:
            time_out = time.time() - evh.dirty_time

            if time_out >= ACT_TIME_OUT:
                os.system(CMD_UNMOUNT)
                time.sleep(1)
                os.system(CMD_SYNC)
                time.sleep(1)
                os.system(CMD_MOUNT)
                evh.reset()

            time.sleep(1)

        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()
