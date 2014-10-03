#!/usr/bin/env python

#  Copyright 2014 Chris Kuethe

import StringIO
from pysssslib import s4_encode, s4_decode

inputstr = StringIO.StringIO("secret12345")
num_shares = 5
num_needed = 3

exitcode = 0
# try this with 0 and 1 incorrect fragments...
for num_bad in range(2):
	shares = []
	for i in xrange(num_shares):
		shares.append(StringIO.StringIO())
	s4_encode(inputstr,shares,num_needed)

	# construct an incorrect fragment by reversing the first fragment
	if num_bad:
		wrong = shares[0].getvalue().encode('hex')
		wrong = wrong[::-1]
		wrong = wrong.decode('hex')
		shares.append(StringIO.StringIO())
		shares[-1].write(wrong)

	# test all-fragments (5), over-determined (4), sufficient (3), insufficient (2)
	while True:
		i = len(shares)
		if ((i - num_bad) < (num_needed - 1)):
			break

		output = StringIO.StringIO()
		try: # decode returns True for success, False for failure
			status = s4_decode(shares,output)
		except: # catch math, IO exceptions and simply mark the test as failed
			status = False

		# expected results:
		# (m <= x <= n) fragments will allow for reassembly
		# (x < m) fragments do not allow for reassembly
		# the presence of incorrect fragments prevents reassembly
		expected = True if ((i >= num_needed) and (num_bad == 0)) else False
		if (status == expected):
			statusmsg = "PASS"
		else:
			exitcode = 1
			statusmsg = "FAIL"

		print "n=%d split=%d/%d bad %d %s" % ((i - num_bad), num_needed, num_shares, num_bad, statusmsg)
		shares.pop(0)

print "Test complete"
exit(exitcode)
