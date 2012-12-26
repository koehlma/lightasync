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

import errno
import socket

import lightasync.platform.globalize as globalize

def server():
    # Setup server socket
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    connection.bind(('127.0.0.1', 4444))
    connection.listen(5)
    def accept(connection):
        # Accept the new connection
        new, address = connection.accept()
        print('New connection from: {}:{}'.format(*address))
        # Create an IO watch for the new connection
        watch = globalize.watch(new)
        # Global buffer
        watch.buffer = b''
        def close():
            # Handle connection close - unregister all handlers and close the
            # socket
            print('Close connection: {}:{}'.format(*address))
            if watch.registered:
                # Only if the watch is registered unregister it
                watch.unregister()
            new.close()
        def write():
            # Handle write events
            try:
                # Get a chunk of data from the buffer
                data = watch.buffer[:4096]
                print('Send data to "{}:{}": {}'.format(address[0],
                                                        address[1],
                                                        data))
                # Write the chunk
                new.send(data)
                watch.buffer = watch.buffer[4096:]
                if not watch.buffer:
                    # If there is no data to write anymore unregister the write
                    # handler - important! if you don't want to consume 100%
                    # CPU
                    watch.write = None
            except socket.error as error:
                # Handle a connection reset error and close the connection
                if error.args[0] == errno.ECONNRESET:
                    close()
                else:
                    raise    
        def read():
            try:
                # Read a chunk of data
                data = new.recv(4096)
                if data:
                    # Add the data to the global buffer
                    print('Received data from "{}:{}": {}'.format(address[0],
                                                                  address[1],
                                                                  data))
                    watch.buffer += data
                    # Register write callback - now there is some data to write
                    watch.write = write
                else:
                    close()
            except socket.error as error:
                # Handle a connection reset error and close the connection
                if error.args[0] == errno.ECONNRESET:
                    close()
                else:
                    raise
        def error():
            # Handle a connection error and close the connection
            close()
        # Register read and error handler - write must only registered if there
        # is actually data to write - otherwise it will consume 100% CPU because
        # it would emit write in every iteration cycle
        watch.error = error
        watch.read = read
    # Register accept as read callback of the server socket and pass the socket
    # as first argument to accept
    globalize.watch(connection, (accept, (connection,)))

if __name__ == '__main__':
    # Get list of available platforms
    available = globalize.available()
    print('Available platforms:')
    for number, platform in enumerate(available, 1):
        print('   [{}] {}'.format(number, platform))
    number = int(input('Please choose one: ')) - 1
    # Load the specified platform globally
    globalize.load(available[number])
    print('Using platform: {}'.format(available[number]))
    # Set up the Echo-Server
    server()
    # Join the main loop
    globalize.start()