# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import sys

import lightasync.callback as callback
import lightasync.loop as loop

class Stream():
    def __init__(self, connection, loop=loop.loop):
        self.connection = connection
        self.connection.setblocking(False)
        self.loop = loop
        self.watcher = loop.watch(self.connection)
    
    def accept(self):
        def activator(callback):
            def accept():
                try:
                    callback.emit(self.connection.accept())
                except Exception:
                    callback.exception = sys.exc_info()
                    callback.emit()
            self.watcher.read = accept
        
        def deactivator(callback):
            self.watcher.read = None
            
        return callback.Callback(activator, deactivator)
    
    def recv(self, length):
        def activator(callback):
            def recv():
                try:
                    callback.emit(self.connection.recv(length))
                except Exception:
                    callback.exception = sys.exc_info()
                    callback.emit()
            self.watcher.read = recv
        
        def deactivator(callback):
            self.watcher.read = None
            
        return callback.Callback(activator, deactivator)
    
    def send(self, data):
        def activator(callback):
            def send():
                try:
                    callback.emit(self.connection.send(data))
                except Exception:
                    callback.exception = sys.exc_info()
                    callback.emit()
            self.watcher.write = send
        
        def deactivator(callback):
            self.watcher.write = None
                    
        return callback.Callback(activator, deactivator)