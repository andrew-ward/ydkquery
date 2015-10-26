#!/usr/bin/env python 
"""
usage: python convert.py INFILE OUTPUT
This is a command line program for converting between deck formats.
INFILE should be a path to a properly formatted .ydk or .txt deck.
	If you do not give an extension, it will be assumed to be .ydk.
	If the deck does not exist, it will search the ygopro/deck directory as specified in yugioh.core.config
If OUTPUT is a path, it will convert and save the new deck file to that path.
	You may also simply give a file format (ydk, md, txt), where instead the output will be printed to stdout.
"""

import sys, os
from yugioh import ygopro, converters, findpath

	
def _find_output(arg):
	""" determine output file location (if any) and format """
	if arg.startswith('.') and arg in converters.OUTPUTS:
		return None, arg
	elif '.'+arg in converters.OUTPUT:
		return None, '.'+arg
	else:
		path, basename = os.path.split(arg)
		deckname, ext = os.path.splitext(basename)
		
		if path == '' and ext == '':
			return ygopro.deck_path(deckname), '.ydk'
		
		elif ext == '':
			return arg+'.ydk', '.ydk'
			
		else:
			return arg, ext
		
if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="A command line program for converting between deck formats.")
	parser.add_argument('input_path', help="a path to a properly formatted .ydk or .txt deck. If you do not give an extension, it will be assumed to be .ydk. If the deck does not exist, it will search the ygopro/deck directory as specified in yugioh.core.config")
	parser.add_argument('output_path', help="The location to save the newly created deck file. You may also simply give a file format (ydk, md, txt), where instead the output will be printed to stdout. If it is merely a deck name, with no extension or path, it will be assumed .ydk, and saved in the ygopro deck directory.")
	
	args = parser.parse_args()
	
	infile = findpath.find_deck(args.input_path)
	infmt = findpath.find_format(args.input_path)
	if infile == None:
		raise RuntimeError('Could not find deck {0}'.format(args.input_path))
		
	outfile, outfmt = _find_output(args.output_path)
	
	result = converters.conversion(infile, infmt, outfmt)
	if result != None:
		if outfile == None:
			sys.stdout.write(result)
		else:
			with open(outfile, 'w') as fl:
				fl.write(result)
	else:
		raise NotImplementedError('Cannot yet convert from {0} to {1}'.format(infmt, outfmt))
