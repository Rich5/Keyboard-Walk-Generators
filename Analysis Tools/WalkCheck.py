'''

    WalkCheck.py - Checks strings and detects keyboard walks
    
    usage: WalkCheck.py [-h] [-l [L]] [-strict] [-loop] [-stats]
                    [graph_file_name] [input]

    Check if string(s) are keyboard walks

    positional arguments:
      graph_file_name      File with adjacency list of format {'letter':
                           {'direction': 'letter connected'}}
      input                File name or single string to check

    optional arguments:
      -h, --help           show this help message and exit
      -l [L], -length [L]  Walk length
      -strict              Only find exact walks of length specified by -l option
      -loop                Consider adjacent dublicate letters as walks
      -stats               Do some calculations
      
    The MIT License (MIT)

    Copyright (c) 2014 Rich Kelley, RK5DEVMAIL[A T]gmail[D O T]com, @RGKelley5, www.frogstarworldc.com
    
    NOTE: File containing graph data structure can be found at https://github.com/Rich5/Keyboard-Walk-Generators/blob/master/Method%201%20-%20Tree%20Walks/qwerty_graph.txt

'''

import argparse
import os.path


def walk_checker(graph, password, length=4, strict=True, loop=False):
    
    result = False
    path_length = 1
    
    if strict and len(password) != length:
        
        return result
    
    for i in range(len(password)):
        
        current_letter = password[i]
        
        if i < len(password)-1:
        
            next_letter = password[i+1]
            
            if current_letter in graph:
                
                if loop:
                
                    if next_letter in graph[current_letter].values():
                
                        path_length += 1
                    
                        if path_length == length:
                            result = True

                    else:
                    
                        result = False
                        path_length = 1
                
                else:
                
                    if next_letter in graph[current_letter].values() and next_letter.lower() != current_letter.lower():
                    
                        path_length += 1
                        
                        if path_length == length:
                            result = True

                    else:
                    
                        result = False
                        path_length = 1
                    
    return result
        
        
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Check if string(s) are keyboard walks')
    parser.add_argument('graph_file_name', nargs='?', help="File with adjacency list of format {'letter': {'direction': 'letter connected'}}", type=str)
    parser.add_argument('input', nargs='?', help="File name or single string to check", type=str)
    parser.add_argument('-l', '-length', nargs='?', help="Walk length", type=int, default=4)
    parser.add_argument('-strict', help="Only find exact walks of length specified by -l option", action='store_true', default=False)
    parser.add_argument('-loop', help="Consider adjacent dublicate letters as walks", action='store_true', default=False)
    parser.add_argument('-stats', help="Do some calculations", action='store_true', default=False)
    args = parser.parse_args()
    
    try:
                
        with open(args.graph_file_name, "r") as fin:
        
            graph = eval(fin.read())

    except IOError as e:

        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        
    
    if os.path.isfile(args.input):
        with open(args.input, "r") as fin:
        
            status = False
            total = 0
            total_true = 0
            for line_num,line in enumerate(fin):
                
                if len(line) >= args.l:
                    
                    total += 1
                    status = walk_checker(graph, line.rstrip('\n\r'), args.l, args.strict, args.loop)
                    
                    if status and not args.stats:
                        print line.rstrip('\n\r')
                        
                    if status and args.stats:
                        total_true += 1
                    

            if args.stats:
                print "Total Possible:\t " + str(total)
                print "Total Walks:\t " + str(total_true), "({0:.1f}%)".format(float(total_true)/float(total) * 100)
                
    else:
    
        status = walk_checker(graph, args.input.rstrip('\n\r'), args.l, args.strict, args.loop)
                
        if status:
            print args.input.rstrip('\n\r')
