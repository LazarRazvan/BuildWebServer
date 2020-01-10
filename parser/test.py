import sys

# count the arguments
arguments = len(sys.argv) - 1

if arguments == 1:
	print ("Da")
print "Length is = %s" % (len(sys.argv))
# output argument-wise
position = 1
while (arguments >= position):
    print ("parameter %i: %s" % (position, sys.argv[position]))
    position = position + 1
