import os
import re
import tempfile
import unittest

from PIL import Image

from pdf_utils import clean_pdf_name, images_to_pdf


class ImagesToPdfTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def make_image(self, name, mode="RGB", size=(120, 80)):
        path = os.path.join(self.folder, name)
        Image.new(mode, size, "white").save(path)
        return path

    def test_creates_one_page_per_image(self):
        paths = [self.make_image("a.png"), self.make_image("b.jpg"), self.make_image("c.png", mode="RGBA")]
        out = os.path.join(self.folder, "out.pdf")
        images_to_pdf(paths, out)
        with open(out, "rb") as f:
            data = f.read()
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", data)), 3)

    def test_empty_list_raises_error(self):
        with self.assertRaises(ValueError):
            images_to_pdf([], os.path.join(self.folder, "out.pdf"))


class CleanPdfNameTests(unittest.TestCase):
    def test_adds_pdf_extension(self):
        self.assertEqual(clean_pdf_name("My notes"), "My notes.pdf")

    def test_does_not_double_the_extension(self):
        self.assertEqual(clean_pdf_name("report.PDF"), "report.pdf")

    def test_removes_characters_windows_does_not_allow(self):
        self.assertEqual(clean_pdf_name('a/b\\c:d*e?f"g<h>i|j'), "abcdefghij.pdf")

    def test_empty_or_only_bad_characters_gives_default_name(self):
        self.assertEqual(clean_pdf_name(""), "images.pdf")
        self.assertEqual(clean_pdf_name("   "), "images.pdf")
        self.assertEqual(clean_pdf_name("???"), "images.pdf")

    def test_keeps_arabic_names(self):
        self.assertEqual(clean_pdf_name("ملخص المحاضرة"), "ملخص المحاضرة.pdf")

    def test_long_names_are_shortened(self):
        self.assertEqual(len(clean_pdf_name("a" * 500)), 100 + len(".pdf"))


if __name__ == "__main__":
    unittest.main()
