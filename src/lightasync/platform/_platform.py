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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import time

import lightasync.platform.exceptions as exceptions

class Timeout():
    def __init__(self, platform, delta, callback, *args, **kwargs):
        self.platform = platform
        self.delta = delta
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.active = False      
    
    def __gt__(self, other):
        if hasattr(other, 'deadline'):
            return self.deadline > other.deadline
        super().__gt__(other)
    
    def __lt__(self, other):
        if hasattr(other, 'deadline'):
            return self.deadline < other.deadline
        super().__lt__(other)     
    
    def activate(self):
        if self.active:
            raise exceptions.TimeoutActive()
        self.active = True
        self.deadline = time.time() + self.delta
    
    def emit(self):
        if self.active == False:
            raise exceptions.TimeoutInactive()
        self.active = False
        self.callback(*self.args, **self.kwargs)
    
    def cancel(self):
        if self.active == False:
            raise exceptions.TimeoutInactive()
        self.active = False

class Watch():
    READ = None
    WRITE = None
    ERROR = None
    
    def __init__(self, platform, fileobj, read=None, write=None, error=None):
        self.platform = platform
        self.fileobj = fileobj
        self._read = read
        self._write = write
        self._error = error
        self.registered = False
    
    def _call(self, callback):
        args = ()
        kwargs = {}
        if isinstance(callback, tuple):
            function = callback[0]
            if len(callback) > 1 and isinstance(callback[1], tuple):
                args = callback[1]
            elif len(callback) > 1 and isinstance(callback[1], dict):
                kwargs = callback[1]
            if len(callback) > 2 and isinstance(callback[2], tuple):
                args = callback[2]
            elif len(callback) > 2 and isinstance(callback[2], dict):
                kwargs = callback[2]            
        else:
            function = callback
        function(*args, **kwargs)            
                
    def register(self):
        if self.registered:
            raise exceptions.WatchRegistered()
        self.registered = True
    
    def modified(self):
        if self.registered == False:
            raise exceptions.WatchUnregistered()
    
    def unregister(self):
        if self.registered == False:
            raise exceptions.WatchUnregistered()
        self.registered = False   
    
    def emit(self, events):
        if events & self.READ:
            if self._read:
                self._call(self._read)
            else:
                self.modified()
        if events & self.WRITE:
            if self._write:
                self._call(self._write)
            else:
                self.modified()
        if events & self.ERROR:
            if self._error:
                self._call(self._error)
            else:
                self.modified()
    
    @property
    def events(self):
        events = 0
        if self._read is not None: events |= self.READ
        if self._write is not None: events |= self.WRITE
        if self._error is not None: events |= self.ERROR
        return events
                   
    @property
    def read(self):
        return self._read
    
    @read.setter
    def read(self, callback):
        none = self._read is None
        self._read = callback
        if (none and callback is not None) or (not none and callback is None):
            self.modified()
    
    @property
    def write(self):
        return self._write
    
    @write.setter
    def write(self, callback):
        none = self._write is None
        self._write = callback
        if (none and callback is not None) or (not none and callback is None):
            self.modified()
        
    @property
    def error(self):
        return self._error
    
    @error.setter
    def error(self, callback):
        none = self._error is None
        self._error = callback
        if (none and callback is not None) or (not none and callback is None):
            self.modified()   
    
class Platform():   
    def __init__(self):
        self.active = False
        
    def timeout(self, delta, callback, *args, **kwargs):
        raise NotImplemented()
    
    def watch(self, fileobj, read=None, write=None, error=None):
        raise NotImplemented()
    
    def start(self):
        if self.active:
            raise exceptions.BackendActive()
        self.active = True
    
    def stop(self):
        if self.active == False:
            raise exceptions.BackendInactive()
        self.active = False