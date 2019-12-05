from solver import *

@timeout_decorator.timeout(5, timeout_exception=StopIteration)
def f():
	while True:
		pass
f()