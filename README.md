# LightAsync
Lightasync aims to be a fast, lightweight, cross platform and multi gui toolkit
library for asynchronous IO. It is written in Python and using Enhanced
Generators as described in PEP 342.

## Working
 * Platforms:
 	* GLib
 	* Epoll

## ToDo:
 * Implement coroutines with Enhanced Generators (PEP 342)
 * Python 2 Support
 * Something like Tornado's stream class
 * Platforms:
 	* PySide
 	* PyQT
 	* plain select (select.select)
 * Cleaning
 
# Enhanced Generator (PEP 342)
	def function_2():
		return Event | Condition | Timeout | Asynchronous | Callback | ...
	
	@asynchronous
	def function_1():
		result = yield function_2(*arguments, **key_word_argument)
					   | - Event: Wait until event occurs and then continue
					   |          execution. Result will be the arguments passed to
					   |		  the event handler.
					   | - Condition: Wait until the condition becomes active and
					   |              continue execution after that. Result will be
					   |			  `None`.
					   | - Timeout: Wait until timeouts time delta is over and then
					   |            continue execution. Result will be `None`
					   | - Asynchronous: Wait until an other asynchronous function
					   |				 has finished and pass its result to result.
					   | - Callback: Wait until callback is called and pass the
					   |			 arguments to result.
					   | - ...: Every other Python object will be stored in the
					   |        asynchronous object's progress variable and could
					   |		be used to dispatch the progress of a certain task. 
				   
	