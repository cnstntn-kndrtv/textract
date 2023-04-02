"""
Process an image file using tesseract.
"""
import os

import easyocr

from .utils import ShellParser

easyocr_reader = easyocr.Reader(['ru','en']) # this needs to run only once to load the model into memory

class TesseractParser(ShellParser):
    """Extract text from various image file formats using tesseract-ocr"""

    def extract(self, filename, **kwargs):

        # if language given as argument, specify language for tesseract to use
        if 'language' in kwargs:
            args = ['tesseract', filename, 'stdout', '-l', kwargs['language']]
        else:
            args = ['tesseract', filename, 'stdout']

        stdout, _ = self.run(args)
        return stdout


class Parser(ShellParser):
    """Extract text from various image file formats using tesseract-ocr"""

    def extract(self, filename, **kwargs):

        result = easyocr_reader.readtext(filename, paragraph=True, y_ths=-0.1)
        text = '\n'.join([r[1] for r in result])

        return text
