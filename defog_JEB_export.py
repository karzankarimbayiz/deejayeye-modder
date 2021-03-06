#!/usr/bin/env python
# 
# https://regex101.com/r/7i9dhC/1 - '\s*const-string.*\s*v[0-9]+\s*,\s*\"([^\"]*)\"\s*' [Match Smalli Files]
# https://regex101.com/r/EFWkGp/3 - '.*?a\.a\("([A-Za-z0-9+\/=]*)".*'                   [Match Java files]
#
# Updated version of https://github.com/Bin4ry/deejayeye-modder/blob/master/decrypt_strings.py
# This version handles JEB exports. 
# https://www.pnfsoftware.com/jeb2/manual/misc/#exporting-output
#
# Mass replace functions from https://stackoverflow.com/a/1597755
# 
# Code mashup by Hostile
# usage: 
# $ python decrypt_JEB_export.py ~/Desktop/DJI418

import os
import re
import sys
import fnmatch
import base64
import binascii

# We are only worrying about the current key 

key = 'Y9*PI8B#gD^6Yhd1'
klen=8

def decrypt(s,l):
        s = base64.decodestring(s)
        decr = ''.join([chr(ord(c) ^ ord(key[i%l*2])) for i,c in enumerate(s)])
        decr = decr.replace('\r', '').replace('\n', '').replace('"', '').replace('\\','')
        return decr

# list of extensions to replace
DEFAULT_REPLACE_EXTENSIONS = (".java")

def try_to_replace(fname, replace_extensions=DEFAULT_REPLACE_EXTENSIONS):
    if replace_extensions:
        return fname.lower().endswith(replace_extensions)
    return True

def file_replace(fname, pat, subpat, check_import):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            return # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            match = re.findall(pat, line)
            if len(match) > 0:            
                for onematch in match:
                    string_fog = (re.search(subpat, onematch)).group(1)
                    try:
                        string_defog = decrypt(string_fog, klen)
                        string_defog = '"'+string_defog+'"'
                    except binascii.Error as err:
                        string_defog = onematch
                        pass
                    #print onematch, string_fog, string_defog
                    line = line.replace(onematch, string_defog);
                out.write(line[:-1])
            else:
                out.write(line)
        out.close()
	print "wrote " + fname
        os.rename(out_fname, fname)

# https://gist.github.com/whophil/2a999bcaf0ebfbd6e5c0d213fb38f489
def recursive_glob(rootdir='.', pattern='*'):
        matches = []
        for root, dirnames, filenames in os.walk(rootdir):
          for filename in fnmatch.filter(filenames, pattern):
                  matches.append(os.path.join(root, filename))
        return matches

def mass_replace(dir_name, replace_extensions=DEFAULT_REPLACE_EXTENSIONS):

#    pat = re.compile('.*?(com\.dji\.f\.a\.a\.b\.a\(\"[A-Za-z0-9+\/=]\"\)).*')
    regex1 = 'com\.dji\.f\.a\.a\.b\.a\("[A-Za-z0-9+\/=]+?"\)'
    regex1_sub = 'com\.dji\.f\.a\.a\.b\.a\("([A-Za-z0-9+\/=]+?)"\)'
    pat1 = re.compile(regex1)
    pat1_sub = re.compile(regex1_sub)
    check_import1 = ""

    regex2 = 'b\.a\("[A-Za-z0-9+\/=]+?"\)'
    regex2_sub = 'b\.a\("([A-Za-z0-9+\/=]+?)"\)'
    pat2 = re.compile(regex2)
    pat2_sub = re.compile(regex2_sub)
    check_import2 = "import com\.dji\.f\.a\.a"

#    pat = re.compile('.*?b\.a\("([A-Za-z0-9+\/=]*)"\).*')

    filenames = recursive_glob(dir_name, "*.java")
    for fname in filenames:
    	if try_to_replace(fname, replace_extensions):
            file_replace(fname, pat1, pat1_sub, check_import1)
            file_replace(fname, pat2, pat2_sub, check_import2)

if len(sys.argv) != 2:
    u = "Usage: mass_replace <dir_name>\n"
    sys.stderr.write(u)
    sys.exit(1)

mass_replace(sys.argv[1])
