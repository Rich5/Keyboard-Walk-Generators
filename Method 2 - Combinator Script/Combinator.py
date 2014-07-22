#!/usr/bin/python

'''

    usage: Combinator.py [-h] [-l [L]] [file_name]

    Combinator: Combine strings into arbitrary length strings

    positional arguments:
      file_name            File with strings of same length

    optional arguments:
      -h, --help           show this help message and exit
      -l [L], -length [L]  Length of final strings
      
    The MIT License (MIT)

    Copyright (c) 2014 Rich Kelley, RK5DEVMAIL[A T]gmail[D O T]com, @RGKelley5

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

'''

import argparse
import copy
from math import ceil

global string_list
global trim_length
global input_length
global file_name

def Combine(length, output):
    
    if length > 0:
    
        with open(file_name, 'r') as f:
    
            for line_num,chunk in enumerate(f):
            
                Combine(length-input_length, output + chunk.rstrip())
    else:
	
		output = output.rstrip()
		print output[:len(output)-trim_length]

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Combinator: Combine strings into arbitrary length strings')
    parser.add_argument('file_name', nargs='?', help="File with strings of same length", type=str)
    parser.add_argument('-l', '-length', nargs='?', help="Length of final strings", type=int, default=1)
    args = parser.parse_args()
    
    length = args.l
    file_name = args.file_name
    
    with open(file_name, 'r') as f:
    
        first_line = f.readline()
        first_line = first_line.rstrip()
        
    input_length = len(first_line)  # Script assumes all lines are the same length
    num_of_copies = int(ceil(float(length)/float(input_length)))
    trim_length = -1*(length - (input_length*num_of_copies))

    Combine(length, "")