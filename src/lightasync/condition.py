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

import lightasync.event as event

class Condition():
    def __init__(self, name=None):
        self.name = name        
        self.changed = event.Event('changed')
        self._state = False
        
    def __enter__(self):
        self.state = True
    
    def __exit__(self, *arguments):
        self.state = False
    
    def __bool__(self):
        return self.state
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state):
        self._state = state
        self.changed.emit(state)
    
    def activate(self):
        self.state = True
    
    def deactivate(self):
        self.state = False