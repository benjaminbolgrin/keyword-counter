import sys
import argparse
import codecs
import re
import requests
from bs4 import BeautifulSoup

# Parse the parameters from the console
parser = argparse.ArgumentParser(description='Counts the occurrence of keywords on a website.')
parser.add_argument('-url', metavar='url', type=str, nargs='?',
                    help='the url')
parser.add_argument('-kw', metavar='kw', type=lambda s: unicode(s, 'utf8'), nargs='+',
                    help='the keywords')
args = parser.parse_args()


class KeywordCounter:

    charset = ''
    url = args.url
    keywords = args.kw
    total_words = ()
    total_percentage = 0

    def __init__(self):
        # Stop if the url is missing
        if self.url is None:
            print("\nError:\nMissing url\n")
            sys.exit()
        try:
            # Connect to the website
            transfer = requests.get(self.url)

            # Get the html from the connection
            html = transfer.text

            # Make a BeautifulSoup object from the html
            bs4_obj = BeautifulSoup(html, 'html.parser')

            # Get the charset meta information from the BeautifulSoup object
            html_meta_charset = bs4_obj.find('meta', charset=True)

            if html_meta_charset:
                self.charset = html_meta_charset['charset']
                if self.encoding_check():

                    # Set the connection encoding to the value of meta charset
                    transfer.encoding = self.charset

                    # Update the html with the new encoding
                    html = transfer.text

                    # Update the BeautifulSoup object
                    bs4_obj = BeautifulSoup(html, 'html.parser')

            # Remove scripts from the BeautifulSoup object
            [ex.extract() for ex in bs4_obj.findAll('script')]

            # Get the text from the body element
            text_string = bs4_obj.find('body').getText(separator=u' ').lower()

            # Get all words
            self.total_words = re.findall(r'\w+', text_string, re.UNICODE)

            print("\n### Keyword Counter Result for '" + self.url + "' ###\n\nTotal number of words: " + str(len(self.total_words)) + "\n")

            if self.keywords:

                for keyword in self.keywords:

                    # Get all words matching the search criteria
                    keyword_matches = re.findall(r'[\W]' + keyword.lower() + r'[\W]', text_string, re.UNICODE)

                    percentage = self.calc_percentage(len(keyword_matches))

                    self.total_percentage += percentage

                    print("Occurrence of '" + keyword + "': " + str(len(keyword_matches)) + " ("+str(percentage)+"%)")

            else:
                print('No keywords given')

            print("\nTotal percentage of given keywords: " + str(self.total_percentage) + "%\n")

        # Catch connection exceptions
        except requests.exceptions.RequestException as e:
            print("\nError:\n" + str(e) + "\n")

    # Checks if the encoding is known
    def encoding_check(self):
        try:
            codecs.lookup(self.charset)
        except LookupError:
            return False
        return True

    def calc_percentage(self, matches):
        percentage = float(matches) / float(len(self.total_words)) * 100
        return round(percentage, 2)

# Run the code of class KeywordCounter
KeywordCounter()
