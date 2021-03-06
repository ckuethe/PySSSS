#!/usr/bin/env python
#
#  Copyright 2010 Mathias Herberts
#  Copyright 2014 Chris Kuethe
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# -*- coding: utf-8 -*-

from pysssslib import s4_encode, s4_decode

if __name__ == "__main__":
  import StringIO
  input = StringIO.StringIO("Too many secrets, Marty!")
  outputs = []
  n = 10
  k = 4
  for i in xrange(n):
    outputs.append(StringIO.StringIO())

  s4_encode(input,outputs,k)

  print "output shares %d-of-%d" % (k, n)
  for i in xrange(n):
	  print str(i)+": "+outputs[i].getvalue().encode('hex')
  print ""

  print "randomly selecting %d shares" % k
  import random
  inputs = []
  randIndex = random.sample(range(n), k)
  for i in randIndex:
    f = outputs[i]
    s = f.getvalue().encode('hex')
    print str(i)+": "+s
    inputs.append(f)
  print ""

  print "decoding shares "
  for i in inputs:
    print i.getvalue().encode('hex')
  output = StringIO.StringIO()
  rvsuccess = s4_decode(inputs,output)
  print ""

  print "decoding insufficient shares "
  inputs.pop()
  for i in inputs:
    print i.getvalue().encode('hex')
  badoutput = StringIO.StringIO()
  rvfail = s4_decode(inputs,badoutput)
  badoutput = badoutput.getvalue()
  print ""

  print "input  text: %s" % input.getvalue()
  print "output text: %s\n\treturn value %d (should be %d)" % (output.getvalue(), rvsuccess, True)
  print "short decode return value %d (should be %d)" % (rvfail, False)
