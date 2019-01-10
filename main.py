import colony as abc
import std_lib as s
# TESTING FUNCTIONS
ubound = [ 5.0, 5.0]
lbound = [-5.0, -5.0]
xbee = abc.Colony(s.sphere, lbound, ubound, 50,2500)

print("Opt_soln = ", xbee.optimize())
