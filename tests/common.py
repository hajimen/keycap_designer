import unittest
from pathlib import Path
import numpy as np
import PIL.Image as PILImageModule
from pdf2image.pdf2image import convert_from_path
from keycap_designer.constants import CURRENT_DIR


def pdf2image(pdf_file: Path):
    return convert_from_path(pdf_file, poppler_path=CURRENT_DIR / 'tests/poppler/Library/bin')


def assert_pdf(self: unittest.TestCase, PDF_FILE: Path, oracle_name: str, show=False, make_oracle=False):
    imgs = pdf2image(PDF_FILE)
    for i, img in enumerate(imgs):
        if show:
            img.show()
            continue
        f = CURRENT_DIR / f'tests/oracle/{oracle_name}_{i}.png'
        if make_oracle:
            img.save(f)
        else:
            oracle = np.array(PILImageModule.open(f), dtype=np.uint8)
            self.assertTrue(np.all(np.isclose(np.array(img, dtype=np.uint8), oracle, atol=1)))
