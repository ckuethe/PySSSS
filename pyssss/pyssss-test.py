#!/usr/bin/env python

# XXX should reassembly be possible with incorrect fragments?

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
		try:
			status = s4_decode(shares,output)
		except:
			status = -1

		expected = 0 if (i >= (num_needed + num_bad)) else -1
		if (status == expected):
			statusmsg = "PASS"
		else:
			exitcode = 1
			statusmsg = "FAIL"

		print "n=%d split=%d/%d bad %d %s" % ((i - num_bad), num_needed, num_shares, num_bad, statusmsg)
		shares.pop(0)

print "Test complete"
exit(exitcode)
