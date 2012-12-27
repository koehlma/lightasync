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

import functools
import sys
import threading

import lightasync.callback as callback
import lightasync.condition as condition
import lightasync.event as event
import lightasync.timeout as timeout

class Asynchronous():
    ASYNCHRONOUS = 0
    THREAD = 1
    
    RUNNING = 0
    WAITING = 1
    
    def __init__(self, mode, function, arguments, keyword_arguments):
        self.mode = mode
        self.function = function
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments
        self.state = self.WAITING
        self.active = False
        self.generator = None
        self.result = None
        self.current = None
        self.handler = None
        self.callback = None
        self.child = None
        self.parent = None
        self.finished = event.Event('finished')
        self.progress = event.Event('progress')
    
    def _next(self, *arguments):
        if self.mode == self.ASYNCHRONOUS:
            self._resume(*arguments)
        elif self.mode == self.THREAD:
            threading.Thread(target=self._resume, args=arguments).start()
    
    def _resume(self, *arguments):
        while True:
            if self.handler is not None:
                self.handler.remove()
                self.handler = None
            elif self.callback is not None:
                call = self.callback
                self.callback = None
                call.deactivate()
                if call.exception:
                    self.throw(*call.exception)                
            if len(arguments) == 1:
                result = arguments[0]
            elif len(arguments) > 1:
                result = arguments
            else:
                result = None
            try:
                self.state = self.RUNNING
                next = self.generator.send(result)
                self.state = self.WAITING     
                if (isinstance(next, callback.Callback) or
                    isinstance(next, timeout.Timeout)):
                    self.callback = next
                    next.activate(self._next)
                    break
                elif isinstance(next, condition.Condition):
                    self.handler = next.changed.handler(self._next)
                    break
                elif isinstance(next, event.Event):
                    self.handler = next.handler(self._next)
                    break
                elif isinstance(next, Asynchronous):
                    next.parent = self
                    self.child = next
                    self.handler = next.finished.handler(self._next)
                    break
                else:
                    self.current = next
                    self.progress.emit(next)               
            except StopIteration as error:
                if len(error.args) == 1:
                    self.result = error.args[0]
                elif len(error.args) > 1:
                    self.result = error.args
                self.finished.emit(self.result)
                self.active = False
                break
            except Exception as error:
                exception, value, traceback = sys.exc_info()
                if self.parent:
                    self.parent.throw(exception, value, traceback)
                else:
                    raise
                break              
    
    def _generate(self):
        self.active = True
        self.generator = self.function(*self.arguments,
                                       **self.keyword_arguments)
        self._resume()
    
    def _thread(self):
        threading.Thread(target=self._generate).start()
    
    def close(self):
        try:
            if self.generator:
                self.generator.close()
        except StopIteration as error:
            if len(error.args) == 1:
                self.result = error.args[0]
            elif len(error.args) > 1:
                self.result = error.args
            self.finished.emit(self.result)
            self.active = False
    
    def throw(self, exception, value=None, traceback=None):
        try:
            if self.generator:
                self.generator.throw(exception, value, traceback)
        except StopIteration as error:
            if len(error.args) == 1:
                self.result = error.args[0]
            elif len(error.args) > 1:
                self.result = error.args
            self.finished.emit(self.result)
            self.active = False            
            
    def start(self):
        if self.mode == self.ASYNCHRONOUS:
            self._generate()
        elif self.mode == self.THREAD:
            self._thread()
        elif self._mode == self.PROCESS:
            self._process()

def asynchronous(function):
    def wrapper(*arguments, **keyword_argumnets):
        asynchronous = Asynchronous(Asynchronous.ASYNCHRONOUS, function,
                                    arguments, keyword_argumnets)
        asynchronous.start()
        return asynchronous
    functools.update_wrapper(wrapper, function)
    return wrapper

def thread(function):
    def wrapper(*arguments, **keyword_argumnets):
        asynchronous = Asynchronous(Asynchronous.THREAD, function,
                                    arguments, keyword_argumnets)
        asynchronous.start()
        return asynchronous
    functools.update_wrapper(wrapper, function)
    return wrapper