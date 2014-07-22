
    Methods to Generate Keyboard Walks for Password Cracking

    Author: Rich Kelley, rk5devmail[A T]gmail[D O T]com, @RGKelley5
--------------------------------------------------------

Overview
--------

The "Method 1 - Tree Walks" folder contains the following files:
- QwertyTreeWalker.py
- qwerty_graph.py

The "Method 2 - Combinator Script" folder contains the following files:
- 4_Walk_seed.txt
- Combinator.py
- walk.rule


Method 1 Usage
--------------

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

    EXAMPLE - Interactive Mode:
    
    python QwertyTreeWalker.py qwerty_graph.txt -l 16 -p 7
    
    Executing the above command will drop you into an interactive status prompt and begin output keyboard walks of length 16 to files located in {working dir}/OUTPUT.
    
    Interative Prompt:
    ------------------
    
    **********************************************************************
    ***************** WARNING: This may take a while *********************
    ***************** Type: [S]tatus [Q]uit ******************************
    **********************************************************************


    [ 8-step walk STARTED at:       2014-07-22-131636 with 8 workers ]
    7134.00000000 walks/sec  Walks: 19889 Walks Left: 57548663119
    
    Once the run is completed (or the user has exited the program with the Q command) the interactive prompt will look like this
    
    **********************************************************************
    ***************** WARNING: This may take a while *********************
    ***************** Type: [S]tatus [Q]uit ******************************
    **********************************************************************


    [ 8-step walk STARTED at:       2014-07-22-131636 with 8 workers ]
    7134.00000000 walks/sec  Walks: 19889 Walks Left: 57548663119
    [ 8-step walk ENDED at:         2014-07-22-131652 ]

    Writing files. Please wait this could take several minutes. [Done]

            [Run Stats]
                    Elasped Time: 0.271800001462 minutes
                    9988.00000000 walks/sec/worker
                    162164 walks generated
                    
    Example STDOUT:
    
    python QwertyTreeWalker.py qwerty_graph.txt -l 16 -p 1 > 16_Walk.txt
    
    Executing the above command will output the following to 16_Walk.txt. NOTE: This will probably NOT complete in your lifetime. Porting this to use GPUs might be able to though. If anyone tries using GPUs please share your results.  
    
    ...
    $bhu8.;[=\`zxXAw
    $bhu8.;[=\`zxXAs
    $bhu8.;[=\`zxXA`
    $bhu8.;[=\`zxXAS
    $bhu8.;[=\`zxXA=
    $bhu8.;[=\`zxXAx
    $bhu8.;[=\`zxXAq
    $bhu8.;[=\`zxXA"
    $bhu8.;[=\`zxXAa
    $bhu8.;[=\`zxXA`
    $bhu8.;[=\`zxXAZ
    $bhu8.;[=\`zxXAQ
    ...
    

Method 2 Usage
--------------

    Commandline Arguments:
    ----------------------
    usage: Combinator.py [-h] [-l [L]] [file_name]

        Combinator: Combine strings into arbitrary length strings

        positional arguments:
          file_name            File with strings of same length

        optional arguments:
          -h, --help           show this help message and exit
          -l [L], -length [L]  Length of final strings
          
    EXAMPLE: To create a dictionary of keyboard walks of length 16 the best results come from combining the seed file into length 8 and then into a 16 length file.

    python Combinator.py 4_Walk_seed.txt -l 8 > 8_Walk.txt
    python Combinator.py 8_Walk.txt -l 16 > 16_Walk.txt

    Executing the above commands should generate a file of around 5GB in size. Then you can input the resulting 16_Walk.txt file and walk.rule file into a password cracker. NOTE: The walk.rule rules were written for oclHashcat, but may work in other crackers such as John. 




