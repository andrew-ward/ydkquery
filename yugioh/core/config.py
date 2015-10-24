"""
this file stores constants that tell the library where to find
certain files on your computer.
"""

DATABASE_PATH = "/home/owner/Applications/ygopro-1.033.6-Percy/cards.cdb"
BANLIST_PATH = "/home/owner/Applications/ygopro-1.033.6-Percy/lflist.conf"
DECK_DIRECTORY = "/home/owner/Applications/ygopro-1.033.6-Percy/deck/"

import os
def confirm(path):
	if not os.path.exists(path):
		raise RuntimeError('{0} does not point to an existing path.'.format(path))
		
confirm(DATABASE_PATH)
confirm(BANLIST_PATH)
confirm(DECK_DIRECTORY)
