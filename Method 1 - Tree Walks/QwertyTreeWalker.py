#!/usr/bin/python

'''

    Version 2.0.0 of QwertyTreeWalker supports two modes to display output, stdout and write-to-files
    
    The main process will parse the qwerty_graph datastructure provided, and split the work among a
    number of worker processes. Each worker process will output a file with the walks generated. If the 
    file size exceeds 524288000 bytes then a new file will be created to continue output. Output by default
    will be located in an OUTPUT folder located in the same directory QwertyTreeWalker.py is being run. 
    
    Commandline Arguments:
    ----------------------
    usage: QwertyTreeWalker.py [-h] [-l [L]] [-p [P]] [-x] [-H] [--stdout][--noplain][file_name]

    Generate walks for Qwerty Keyboard

    positional arguments:
      file_name             File with adjacency list of format {'letter':{'direction': 'letter connected'}}

    optional arguments:
      -h, --help                show this help message and exit
      -l [L], -length [L]       Walk length
      -p [P], -processes [P]    Number of processses to divide work
      -x, -exclude              Will trigger prompt for link exclude list
      -H, -hash                 Output NTLM hash
      --stdout                  Output to screen
      --noplain                 Do not print plain text hash

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

from math import ceil
from datetime import datetime, timedelta
from multiprocessing import Process, Manager, freeze_support
from msvcrt import getch
import threading
import hashlib
import binascii
import argparse
import time
import sys
import os
import copy

__version__ = "2.0.0"

class QwertyTreeWalker:

    graph = {}
    start_time = 0
    chunks = 0
    max_depth = 0
    num_workers = 0
    exclude_list = []
    hash = False
    no_plain = True
    
    def __init__(self, graph_data=None, build_exclude=False, plain=True, hash=False, stdout=False):
    
        self.hash = hash
        self.no_plain = plain
        self.stdout = stdout
        
        # All output will be located in the output folder
        self.out_folder = "OUTPUT"
        manager = Manager()
        self.stats = manager.dict()
        
        if not os.path.exists(self.out_folder):
            os.makedirs(self.out_folder)
        
        try:
            
            with open(graph_data, "r") as self.fin:
            
                self.graph = eval(self.fin.read())

        except IOError as e:
        
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

        # Build exclude list if necessary
        if build_exclude:
        
            option = 1
            menu = {}
            for direction in self.graph[self.graph.keys()[0]]:
            
                menu[option] = direction
                option += 1
            
            
            for opt in sorted(menu):
            
                print "[" + str(opt) +"] " + menu[opt]
            
            print "Enter Links to exclude as csv (EX:1,2,3)"
            exclude_list_entered = raw_input(">> ")
            
            try:
            
                exclude_keys = tuple(exclude_list_entered.split(","))
                exclude_list = []
                for key in exclude_keys:
            
                    exclude_list.append(menu[int(key)])
            
                self.exclude_list = exclude_list
                
            except KeyError as e:
            
                pass
            
    def start_workers(self, num_of_processes=1, max_depth=1):
    
        letters = [key for key in self.graph]
        
        self.num_workers = int(ceil(len(letters)/num_of_processes))
        work_chunks = [letters[x:x + self.num_workers] for x in xrange(0,len(letters), self.num_workers)]
        
        # Print start message stats
        self.chunks = len(work_chunks)
        self.max_depth = max_depth
        self.start_time = time.time()
        
        if not self.stdout:
            print "\n\n**********************************************************************"
            print "***************** WARNING: This may take a while *********************"
            print "***************** Type: [S]tatus [Q]uit ******************************"
            print "**********************************************************************\n\n"
            print "[ " + str(self.max_depth) + "-step walk STARTED at:\t" + time.strftime("%Y-%m-%d-%H%M%S") + " with " + str(self.chunks) + " workers ]"
        
        if self.exclude_list:
        
            print "\nExcluding: \n" + str(self.exclude_list) + "\n at user request\n"
            
        
        # Spawn worker processes
        
        pid = 0
        procs = []
        for chunk in work_chunks:
        
            p = Process(target=self.start_walking, args=(max_depth,pid,chunk))
            p.daemon = True
            procs.append(p)
            self.stats[pid] = {'start_time': None, 'total_walks': None, 'walk_rate': 0, 'walks_generated': 0, 'walks_left': None, 'seconds_left': None, 'done': "GO"}
            p.start()
            pid += 1
        
        # Now collect stats and print reports
        time.sleep(2) # Let the other processes get going
        EXIT = False
        self.KILL = False
        
        if not self.stdout:
        
            t = threading.Thread(target=self.input_handler) # Listen for user input during run
            t.daemon = True
            t.start()
        
        while EXIT == False and self.KILL == False:
            
            workers_working = len(work_chunks)
            for stat in self.stats.values():
                
                if stat['done'] == "STOP":
                    
                    workers_working -= 1
                    
                if workers_working <= 0:
                
                    EXIT = True
                    break


        end_time = time.time()
        
        if not self.stdout:
        
            print "\n[ " + str(self.max_depth) + "-step walk ENDED at: \t" + time.strftime("%Y-%m-%d-%H%M%S") +" ]\t\t"
            print "\nWriting files. Please wait this could take several minutes.",
            self.print_end_stats(end_time)
        
        if self.KILL == False:
        
            for p in procs:
                
                p.join()
                
        else:
        
            for p in procs:
                
                p.terminate()
            
        
        
    def print_end_stats(self, end_time):
    
        # Print end message stats
        
        sec = 0
        walks_left = 0
        walk_rate = 0.
        walks_generated = 0
        
        for stat in iter(self.stats.keys()):
            
            walks_generated += long(self.stats[stat]['walks_generated'])
            sec += long(self.stats[stat]['seconds_left'])
            walks_left += long(self.stats[stat]['walks_left'])
            walk_rate += long(self.stats[stat]['walk_rate'])
            start_time = self.stats[stat]['start_time']
        
        avg_walk_rate = walk_rate/self.chunks
        
        print "[Done]"
        print "\n\t[Run Stats]"
        print "\t\tElasped Time: " + str((end_time-self.start_time)/60) + " minutes"
        print "\t\t" + '{0:.8f}'.format(avg_walk_rate) + " walks/sec/worker"
        print "\t\t" + str(walks_generated) + " walks generated\n\n"
        
        
    def report_stats(self, pid, total_walks, walk_rate, walks_generated, walks_left, seconds_left, done): 
        
        stats = {}
        stats = self.stats[pid]
        stats['total_walks'] = total_walks
        stats['walk_rate'] = walk_rate
        stats['walks_generated'] = walks_generated
        stats['walks_left'] = walks_left
        stats['seconds_left'] = seconds_left
        stats['done'] = done
        self.stats[pid] = stats
        
    def print_inc_stats(self): 
    
        sec = 0
        walks_left = 0
        walk_rate = 0.
        walks_generated = 0
        
        for stat in iter(self.stats.keys()):
            
            walks_generated += long(self.stats[stat]['walks_generated'])
            sec += long(self.stats[stat]['seconds_left'])
            walks_left += long(self.stats[stat]['walks_left'])
            walk_rate += long(self.stats[stat]['walk_rate'])
            start_time = self.stats[stat]['start_time']
        
        
        print '\r{0:.8f} walks/sec\t Walks: {1} Walks Left: {2}'.format(walk_rate, walks_generated, walks_left),
        sys.stdout.write("\r")
        sys.stdout.flush()

    def start_walking(self, max_depth, pid, letters=None):
    
        if letters == None:
        
            letters = [key for key in self.graph]

        
        total_walks = self.walks_to_completion(max_depth, letters)
        max_depth = max_depth - 1   # Decrement to account for start at zero
        walks_generated = 0
        
        # Create output file with name format <walk length>_Walk_<time stamp>.txt
        out_file = self.out_folder + os.path.sep + str(max_depth + 1) + "_Walk_" + str(time.strftime("%Y-%m-%d-%H%M%S")) +  "PID-" + str(pid) + "-0.txt"
        fout = open(out_file, "a")
        
        start_time = time.time()
        
        # Initalize stats values
        self.stats[pid] = {'start_time': start_time, 'total_walks': total_walks, 'walk_rate': 0, 'walks_generated': 0, 'walks_left': None, 'seconds_left': None, 'done': "GO"}
        
        #
        # Begin walking about cycling through the graph data structure
        #
        time.sleep(1)
        sub_file = 0
        for letter in letters:
            
            walks_generated = self.walk(pid, fout, 0, max_depth, letter, total_walks, [], walks_generated)
            file_size = os.path.getsize(out_file)
            
            if file_size > 524288000:
            
                fout.close()
                sub_file += 1
                out_file = out_file[:len(out_file)-6] + "-" + str(sub_file) + ".txt"
                fout = open(out_file, "a")

        
        fout.flush()
        fout.close()
        stats = {}
        stats = self.stats[pid]
        stats['done'] = "STOP"
        self.stats[pid] = stats
        
            

    def walk(self, pid, fout, current_depth, max_depth, current_node, total_walks, path_stack=[], walks_generated=0):

        
        path_stack.append(current_node)
        
        if current_depth >= max_depth:
        
            plain_text = ''.join(path_stack)
            ascii_hash = ""
            
            if self.hash:   # Handles the -H arg
            
                hash = hashlib.new('md4', plain_text.encode('utf-16le')).digest()
                ascii_hash = binascii.hexlify(hash)

            if self.no_plain:  # Handles the --noplain
            
                plain_text = ""
            
            else:
            
                plain_text = plain_text + "\t"
            
            
            if not self.stdout:
            
                fout.write(plain_text+ascii_hash)    
                fout.write("\n")
                fout.flush()
            
            else:
                print plain_text+ascii_hash
            
            # calculate and report performance stats
     
            walks_generated += 1
            walks_left = total_walks - walks_generated
            walks_ = float(walks_generated)
            walk_rate = walks_/(time.time()-self.stats[pid]['start_time'])
            seconds_left = long(ceil(walks_left/walk_rate))
            
            self.report_stats(pid, total_walks, walk_rate, walks_generated, walks_left, seconds_left, "GO")
            
            return walks_generated
            
        else:
        
            next_level = current_depth + 1
            
            for direction in self.graph[current_node]:
                
                # Recusive call to walk the graph
                if not direction in self.exclude_list:
                
                    walks_generated = self.walk(pid, fout, next_level, max_depth, self.graph[current_node][direction], total_walks, path_stack, walks_generated)
                    path_stack.pop()

            return walks_generated  # walks_generated return for stats purposes only
        
    def walks_to_completion(self, walk_length, graph):
    
        '''
            Calculate total walks: (e^n-1)v
            where, e = # of edges
                   v = # of vertices
                   n = length of walk
            
        '''
        
        num_of_edges = len(self.graph[self.graph.keys()[0]]) - len(self.exclude_list)    # Grab the first element and count links
        return int(ceil((num_of_edges**(walk_length-1))*len(graph)))
    
    def input_handler(self):
    
        while True:
        
            if ord(getch()) == 115:   # s for status

                self.print_inc_stats()
        
            elif ord(getch()) == 113: # q to quit
            
                self.KILL = True
                break
                
        return

if __name__ == "__main__":

    if sys.platform.startswith('win'):
        freeze_support()
        
    parser = argparse.ArgumentParser(description='Generate walks for Qwerty Keyboard')
    parser.add_argument('file_name', nargs='?', help="File with adjacency list of format {'letter': {'direction': 'letter connected'}}", type=str)
    parser.add_argument('-l', '-length', nargs='?', help="Walk length", type=int, default=2)
    parser.add_argument('-p', '-processes', nargs='?', help="Number of processses to divide work", type=int, default=1)
    parser.add_argument('-x', '-exclude', help="Will trigger prompt for link exclude list", action='store_true')
    parser.add_argument('-H', '-hash', help="Output NTLM hash for testing", action='store_true', default=False)
    parser.add_argument('--stdout', help="Output to screen", action='store_true', default=False)
    parser.add_argument('--noplain', help="Do not print plain text hash", action='store_true', default=False)
    args = parser.parse_args()
    
    if args.p > 1 and args.stdout:
        print "ERROR: Only 1 process allowed when using stdout"
        sys.exit(1)
        
    walker = QwertyTreeWalker(args.file_name,args.x,args.noplain,args.H,args.stdout)
    walker.start_workers(args.p, args.l)