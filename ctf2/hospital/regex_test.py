#Author: Abhay Bhargav
#Date: 20 July 2013

"""
Usage:	
	regex_test.py [-R REGEX] [-W WORD]
	regex_test.py [--email|--username] [-W WORD]
	regex_test.py -h | --help

Options:	
	-h | --help		Show this screen	
	-R REGEX 	Regex pattern to perform check
	--email		Regex pattern automatically checks word for email
	--username	Regex pattern automatically checks word for username
	-W WORD 	Word to match
"""


import re
from docopt import docopt

def test_regex(regex, string):
	pattern = re.compile(regex, re.M|re.I)
	results = re.findall(pattern, string)
	if results == []:
		print "no match found."
	else:
		for result in results:
			print "found match: '%s' against regex pattern '%s'" % (result, regex)

		sanitized = re.sub(pattern, '', string)
		print "Unsanitary Characters: %s" % sanitized
		



def main():	
	arguments = docopt(__doc__)

	if arguments['-R']:
		regex = arguments['REGEX']
	elif arguments['--email']:
		regex = '\\b[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}\\b'
	elif arguments['--username']:
		regex = "[a-zA-Z0-9\-_.]{1,50}"

#	regex = arguments['REGEX']
	word = arguments['WORD']

	

	test_regex(regex, word)

if __name__ == '__main__':main()
