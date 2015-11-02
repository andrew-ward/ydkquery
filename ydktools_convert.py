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
import yugioh

INPUT = {}
OUTPUT = {}

def importer(fmt):
	def decorate(f):
		INPUT[fmt] = f
		return f
	return decorate
	
def exporter(fmt):
	def decorate(f):
		OUTPUT[fmt] = f
		return f
	return decorate
	
def convert(infile, src, dest):
	if src in INPUT:
		deck = INPUT[src](infile)
		if dest in OUTPUT:
			return OUTPUT[dest](deck)
	return None

@importer('.ydk')
def from_ydk(infile):
	return yugioh.ygopro.load_deck(infile)

@importer('.txt')
def from_decklist(infile):
	return yugioh.decklist.load_deck(infile)

@exporter('.txt')
def as_decklist(deck):
	return deck.as_decklist()
	
@exporter('.ydk')
def as_ydk(deck):
	return deck.as_ydk()

@exporter('.md')
def as_markdown(deck):
	return deck.as_markdown()
	
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
			return yugioh.ygopro.deck_path(deckname), '.ydk'
		
		elif ext == '':
			return arg+'.ydk', '.ydk'
			
		else:
			return arg, ext
		
def main(args):
	infile = yugioh.findpath.find_deck(args.input_path)
	infmt = yugioh.findpath.find_format(args.input_path)
	if infile == None:
		raise RuntimeError('Could not find deck {0}'.format(args.input_path))
		
	outfile, outfmt = _find_output(args.output_path)
	
	result = convert(infile, infmt, outfmt)
	if result != None:
		if outfile == None:
			sys.stdout.write(result)
		else:
			with open(outfile, 'w') as fl:
				fl.write(result)
	else:
		raise NotImplementedError('Cannot yet convert from {0} to {1}'.format(infmt, outfmt))
