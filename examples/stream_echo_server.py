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

import socket

import lightasync.platform.globalize as globalize
globalize.load('epoll')

import lightasync.asynchronous as asynchronous
import lightasync.loop as loop
import lightasync.stream as stream

@asynchronous.asynchronous
def read_write(connection):
    server = stream.Stream(connection)
    try:
        while True:
            data = yield server.recv(4096)
            yield server.send(data)
    except Exception as error:
        print(error)

@asynchronous.asynchronous
def server():
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    connection.bind(('127.0.0.1', 4444))
    connection.listen(5)
    server = stream.Stream(connection)
    while True:
        connection, address = yield server.accept()
        read_write(connection)    

if __name__ == '__main__':
    server()
    loop.start()
