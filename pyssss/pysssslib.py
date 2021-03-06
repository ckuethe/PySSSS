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

import random

from GF256elt import GF256elt
from PGF256 import PGF256
from PGF256Interpolator import PGF256Interpolator

def pickRandomPolynomial(degree,zero):
  """Pick a random PGF256 polynomial P such that P(0) = zero"""
   
  coeffs = []
  
  # Set f(0)
  coeffs.append(zero)
  
  # Pick coefficients for x^n with n < degree
  
  for c in xrange(1,degree):
    coeffs.append(GF256elt(random.randint(0,255)))
          
  # Pick non null coefficient for x^degree
  
  coeffs.append(GF256elt(random.randint(1,255)))
  
  return PGF256(coeffs)


def _s4_encodeByte(byte,n,k):
  # Allocate array to track duplicates
  picked = [False for i in xrange(0,256)]
  
  # Pick a random polynomial
  P = pickRandomPolynomial(k-1,GF256elt(byte))
  
  # Generate the keys
  keys = ["" for i in xrange(0,n)]
  
  for i in xrange(0,n):

    #        
    # Pick a not yet picked X value in [0,255],
    # we need a value in [1,255] but to have a credible entropy for bytes we pick it in [0,255]
    # and simply output garbage if we picked 0
    # If we do not do that then the output keys will NEVER have 00 in even positions (starting
    # at 0) which would be a little suspicious for some random data
    #
        
    pick = random.randint(1,255)
            
    while picked[pick] or pick == 0:
      # 0 values will be discarded but output it anyway with trailing garbage
      if pick == 0:
        keys[i] += chr(0)
        keys[i] += chr(random.randint(0,255))
          
      pick = random.randint(1,255)
    
    # Keep track of the value we just picked    
    picked[pick] = True
    
    X = GF256elt(pick)
    Y = P.f(X)
    
    keys[i] += chr(int(X))
    keys[i] += chr(int(Y))

  return keys

def s4_encode(data,outputs,k):
      
  n = len(outputs)

  # Inject signature
  for char in list('GF256OK_'):
    byte = ord(char)
    charkeys = _s4_encodeByte(byte,n,k)
    for i in xrange(0,n):
      outputs[i].write(charkeys[i])

  # Loop through the chars        
  while True:
    char = data.read(1)
    if 0 == len(char):
      break
    byte = ord(char)
    
    charkeys = _s4_encodeByte(byte,n,k)

    for i in xrange(0,n):
      outputs[i].write(charkeys[i])

def s4_decode(keys,output):
  
  interpolator = PGF256Interpolator()
  zero = GF256elt(0)
  
  data = ""
  
  for i in keys:
    i.seek(0)

  # End Of Key    
  eok = False

  while not eok:
    points = []
    for i in xrange(0,len(keys)):
      while True:
        b = keys[i].read(1)
        if 0 == len(b):
          eok = True
          break
        # Skip points with X value of 0, they were added to respect the entropy of the output
        X = ord(b)
        if 0 == X:
          keys[i].seek(keys[i].tell() + 1)
        else:
          break

      if eok:
        break
      
      # Extract X/Y
      Y = ord(keys[i].read(1))
      
      # Push point
      points.append((GF256elt(X),GF256elt(Y)))

    if eok:
      if 0 != i:
        raise Exception('Unexpected EOF while reading key %d' % i)
      break                        

    # Decode next byte
    byte = interpolator.interpolate(points).f(zero)
    data += chr(byte)

  # check for successful decode
  signature = data[0:8]
  data = data[8:]
  rv = True if ('GF256OK_' in signature) else False

  output.write(data)
  output.seek(0)
  return rv
