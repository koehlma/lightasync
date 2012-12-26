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

try:
    from gi.repository import GLib as glib
    available = True
except ImportError:
    available = False

import lightasync.platform._platform as platform

class Timeout(platform.Timeout):        
    def emit(self):
        super().emit()
        return False
    
    def activate(self):
        super().activate()
        self.source = glib.timeout_add(self.delta * 1000, self.emit)
        
    def cancel(self):
        super().cancel()
        glib.source_remove(self.source)

class Watch(platform.Watch):
    READ = glib.IOCondition.IN
    WRITE = glib.IOCondition.OUT
    ERROR = glib.IOCondition.ERR | glib.IOCondition.HUP

    def _emit(self, source, condition):
        self.emit(condition)
        return True
    
    def register(self):
        super().register()
        self.source = glib.io_add_watch(self.fileobj, self.events, self._emit)
    
    def modified(self):
        super().modified()
        glib.source_remove(self.source)
        self.source = glib.io_add_watch(self.fileobj, self.events, self._emit)
    
    def unregister(self):
        super().unregister()
        glib.source_remove(self.source)     

class Platform(platform.Platform):
    def __init__(self):
        super().__init__()
        self._loop = glib.MainLoop()
    
    def timeout(self, delta, callback, *args ,**kwargs):
        timeout = Timeout(self, delta, callback, *args, **kwargs)
        timeout.activate()
        return timeout
    
    def watch(self, fileobj, read=None, write=None, error=None):
        watch = Watch(self, fileobj, read, write, error)
        watch.register()
        return watch
    
    def start(self):
        super().start()
        self._loop.run()
    
    def stop(self):
        super().stop()
        self._loop.quit()