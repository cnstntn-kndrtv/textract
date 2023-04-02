import os
import shutil
from distutils.spawn import find_executable
from tempfile import mkdtemp

import six

from ..exceptions import ShellError, UnknownMethod
from .image import Parser as EasyOcrParser
from .image import TesseractParser
from .utils import ShellParser


class Parser(ShellParser):
    """Extract text from pdf files using either the ``pdftotext`` method
    (default) or the ``pdfminer`` method.
    """

    def extract(self, filename, method='', **kwargs):
        if method == '' or method == 'pdftotext':
            try:
                return self.extract_pdftotext(filename, **kwargs)
            except ShellError as ex:
                # If pdftotext isn't installed and the pdftotext method
                # wasn't specified, then gracefully fallback to using
                # pdfminer instead.
                if method == '' and ex.is_not_installed():
                    return self.extract_pdfminer(filename, **kwargs)
                else:
                    raise ex

        elif method == 'pdfminer':
            return self.extract_pdfminer(filename, **kwargs)
        elif method == 'tesseract':
            return self.extract_ocr(filename, TesseractParser, **kwargs)
        elif method == 'easyocr':
            return self.extract_ocr(filename, EasyOcrParser, **kwargs)
        else:
            raise UnknownMethod(method)

    def extract_pdftotext(self, filename, **kwargs):
        """Extract text from pdfs using the pdftotext command line utility."""
        if 'layout' in kwargs:
            args = ['pdftotext', '-layout', filename, '-']
        else:
            args = ['pdftotext', filename, '-']
        stdout, _ = self.run(args)
        return stdout

    def extract_pdfminer(self, filename, **kwargs):
        """Extract text from pdfs using pdfminer."""
        #Nested try/except loops? Not great
        #Try the normal pdf2txt, if that fails try the python3
        # pdf2txt, if that fails try the python2 pdf2txt
        pdf2txt_path = find_executable('pdf2txt.py')
        try:
            stdout, _ = self.run(['pdf2txt.py', filename])
        except OSError:
            try:
                stdout, _ = self.run(['python3',pdf2txt_path, filename])
            except ShellError:
                stdout, _ = self.run(['python2',pdf2txt_path, filename])
        return stdout

    def extract_ocr(self, filename, ocr_cls, **kwargs):
        """Extract text from pdfs using tesseract (per-page OCR)."""
        temp_dir = mkdtemp()
        base = os.path.join(temp_dir, 'conv')
        contents = []
        try:
            stdout, _ = self.run(['pdftoppm', filename, base])

            for page in sorted(os.listdir(temp_dir)):
                page_path = os.path.join(temp_dir, page)
                page_content = ocr_cls().extract(page_path, **kwargs)
                contents.append(page_content)
            if ocr_cls == TesseractParser:
                return six.b('').join(contents)
            elif ocr_cls == EasyOcrParser:
                return '\n'.join(contents)

        finally:
            shutil.rmtree(temp_dir)
