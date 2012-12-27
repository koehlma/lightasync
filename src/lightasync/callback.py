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

class Callback():
    def __init__(self, activator, deactivator):
        self.activator = activator
        self.deactivator = deactivator
        self.callback = None
        self.exception = None
    
    def activate(self, callback):
        self.callback = callback
        self.activator(self)
            
    def deactivate(self):
        self.deactivator(self)
        self.callback = None
    
    def emit(self, *arguments, **keyword_arguments):
        self.callback(*arguments, **keyword_arguments)