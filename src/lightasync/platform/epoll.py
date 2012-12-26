# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import heapq
import os
import select
import time

import lightasync.platform._platform as platform

if hasattr(select, 'epoll'):
    available = True
else:
    available = False

class Waker():
    def __init__(self):
        read, write = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        self.rfile = os.fdopen(read, 'rb', 0)
        self.wfile = os.fdopen(write, 'wb', 0)
    
    def fileno(self):
        return self.rfile.fileno()
    
    def wake(self):
        self.wfile.write(b'.')
    
    def clear(self):
        self.rfile.read()
    
    def close(self):
        self.wfile.close()
        self.rfile.close()

class Timeout(platform.Timeout):    
    def activate(self):
        super().activate()
        heapq.heappush(self.platform.timeouts.append, self)
        
    def cancel(self):
        super().deactivate()
        self.platform.timeouts.remove(self)

class Watch(platform.Watch):
    READ = select.EPOLLIN
    WRITE = select.EPOLLOUT
    ERROR = select.EPOLLERR | select.EPOLLHUP
        
    def register(self):
        super().register()
        self.platform.watchers[self.fileobj.fileno()] = self
        self.platform.poller.register(self.fileobj, self.events)
    
    def modified(self):
        super().modified()
        self.platform.poller.modify(self.fileobj, self.events)
    
    def unregister(self):
        super().unregister()
        del self.platform.watchers[self.fileobj.fileno()]
        self.platform.poller.unregister(self.fileobj)  

class Platform(platform.Platform):    
    def __init__(self):
        super().__init__()
        self._waker = Waker()
        self.poller = select.epoll()
        self.timeouts = []
        self.watchers = {}
        self.watch(self._waker, self._waker.clear)
    
    def timeout(self, delta, callback, *args, **kwargs):
        timeout = Timeout(self, delta, callback, *args, **kwargs)
        timeout.activate()
        return timeout
    
    def watch(self, fileobj, read=None, write=None, error=None):
        watch = Watch(self, fileobj, read, write, error)
        watch.register()
        return watch
    
    def start(self):
        super().start()
        while self.active:
            poll_timeout = -1
            while self.timeouts:
                now = time.time()
                timeout = self.timeouts[0]              
                if timeout.active.is_set():
                    if timeout.deadline <= now:
                        timeout.emit()
                        heapq.heappop(self.timeouts)
                    else:
                        poll_timeout = timeout.deadline - now
                        break
                else:
                    heapq.heappop(self.timeouts)
            for fd, events in self.poller.poll(poll_timeout):
                if fd in self.watchers:
                    self.watchers[fd].emit(events)   
    
    def stop(self):
        super().stop()
        self._waker.wake()