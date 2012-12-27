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

import lightasync.platform.globalize as globalize

if not globalize.loaded:
    globalize.automatic()

class Loop():
    def __init__(self, platform=globalize.platform):
        self.platform = platform
    
    def timeout(self, delta, callback, *args, **kwargs):
        return self.platform.timeout(delta, callback, *args, **kwargs)
    
    def watch(self, fileobj, read=None, write=None, error=None):
        return self.platform.watch(fileobj, read, write, error)
    
    def start(self):
        self.platform.start()
    
    def stop(self):
        self.platform.stop()

loop = Loop()
timeout = loop.timeout
watch = loop.watch
start = loop.start
stop = loop.stop