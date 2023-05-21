"""
Process an image file using tesseract.
"""
import os

import easyocr

from .utils import ShellParser


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

    def __init__(self,
                 use_gpu: bool = False,
                 delete_reader: bool = True,
                 ) -> None:

        self.use_gpu = use_gpu
        self.delete_reader = delete_reader
        self.reader = self._init_reader()
        super().__init__()

    def _init_reader(self) -> easyocr.Reader:
        return easyocr.Reader(['ru','en'], gpu=self.use_gpu)

    def extract(self, filename, **kwargs):

        result = self.reader.readtext(filename, paragraph=True, y_ths=-0.1)
        text = '\n'.join([r[1] for r in result])

        if self.delete_reader:
            del self.reader

        return text
