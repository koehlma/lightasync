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

import heapq

class Handler():
    LOW = 50
    NORMAL = 0
    HIGH = -50
    
    def __init__(self, event, priority, function, arguments, keyword_arguments):
        self._priority = priority
        self.event = event
        self.function = function
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments
    
    def __gt__(self, other):
        if isinstance(other, Handler):
            return other._priority < self._priority
        elif isinstance(other, int):
            return other < self._priority
        super().__gt__(other)
    
    def __lt__(self, other):
        if isinstance(other, Handler):
            return other._priority > self._priority
        elif isinstance(other, int):
            return other > self._priority
        super().__lt__(other)
    
    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, priority):
        self._priority = priority
        heapq.heapify(self.event.handlers)
    
    def call(self, *arguments,  **keyword_arguments):
        arguments = list(arguments)
        arguments.extend(self.arguments)
        keyword_arguments.update(self.keyword_arguments)
        self.function(*arguments, **keyword_arguments)
    
    def remove(self):
        self.event.handlers.remove(self)

class Event():    
    def __init__(self, name=None):
        self.name = name
        self.handlers = []
    
    def handler(self, function, *arguments, priority=Handler.NORMAL,
                **keyword_arguments):
        handler = Handler(self, priority, function, arguments,
                          keyword_arguments)
        heapq.heappush(self.handlers, handler)
        return handler 
        
    def emit(self, *arguments, **keyword_arguments):
        for handler in self.handlers:
            handler.call(*arguments, **keyword_arguments)