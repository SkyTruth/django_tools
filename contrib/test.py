#!/usr/bin/python
################################################################################
## DATE: 2010-10-26
## AUTHOR: Matt Reid
## MAIL: mreid@kontrollsoft.com
## SITE: http://kontrollsoft.com
## LICENSE: BSD http://www.opensource.org/licenses/bsd-license.php
################################################################################

from __future__ import division
import threading
import sys
import urllib2
import select
import random
import string
import getopt
import time

class threader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global url
        global per
        global u
        for i in range(per):
            if wait > 0:
                time.sleep(wait)
            str = randstr(32)
            # IMPORTANT: this is where we append the search string to the main URL
            # you might need to change this for your site. 
            url = u % {"rand": str}
            print "polling url: %s"%(url)
            urllib2.urlopen(url)
        
def randstr(length):
    global url
    twoletters = [c+d for c in string.letters for d in string.letters]
    r = random.random
    n = len(twoletters)
    l2 = length//2
    lst = [None] * l2
    for i in xrange(l2):
        lst[i] = twoletters[int(r() * n)]
        if length & 1:
            lst.append(random.choice(string.letters))

    return "".join(lst)
            
def init_thread():    
    backgrounds = []
    for thread in range(threads):
        print "Spawning thread: %s"%(thread)
        background = threader()        
        background.start()
        backgrounds.append(background)
    for background in backgrounds:
        background.join()

def print_help():
    print '''loader.py - URL load test script
==================================================
Date: 2010-08-26
Website: http://themattreid.com
Author: Matt Reid
Email: themattreid@gmail.com
License: new BSD license
==================================================
Use the following flags to change default behavior
    
   Option                 Description
   --url=                 URL to test
   --per-connection=      Number of sequential reqests per connection (default 2)
   --threads=             Number of threads for url connections (default 50)
   --wait=                Time to wait in-between requests
   --help                 Print this message

   -u                     Same as --url
   -p                     Same as --per-connection
   -t                     Same as --threads
   -w                     Same as --wait
   -h                     Same as --help
   '''


def main():    
    init_thread()
    sys.exit(0)

if __name__ == "__main__":
    global threads #num threads/connections to open
    global u #url to hit
    global per #per connection url hits
    try:
        options, remainder = getopt.getopt(
            sys.argv[1:], 'ptuw', ['per-connection=',
                                   'threads=',
                                   'url=',
                                   'wait=',
                                   'help'])
    except getopt.GetoptError, err:
        print str(err) 
        sys.exit(2)
        
    for opt, arg in options:
        if opt in ('--per-connection'):
            per = int(arg)
        elif opt in ('--threads'):
            threads = int(arg)
        elif opt in ('--url'):
            u = arg
        elif opt in ('--wait'):
            wait = int(arg)
        elif opt in ('--help'):
            print_help()
            sys.exit(2)

    try:
        threads
    except NameError:
        print "No thread quantity specified."
        print_help()
        sys.exit(2)
    try:
        per
    except NameError:
        per = 2
    try:
        u
    except NameError:     
        print "No URL Specified"
        print_help()
        sys.exit(2)
    try:
        wait
    except NameError:
        wait=0
    
    main()
