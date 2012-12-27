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

import lightasync.platform.glib
import lightasync.platform.epoll

platforms = {'glib' : lightasync.platform.glib,
             'epoll' : lightasync.platform.epoll}

loaded = False

Platform = None

platform = None
timeout = None
watch = None
start = None
stop = None

def load(name):
    global loaded
    
    global Platform
    
    global platform, timeout, watch, start, stop
    
    loaded = True
    
    Platform = platforms[name].Platform
    
    platform = Platform()
    timeout = platform.timeout
    watch = platform.watch
    start = platform.start
    stop = platform.stop

def available():    
    return [name for name, platform in platforms.items() if platform.available]

def automatic():
    load(available()[0])