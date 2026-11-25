import unittest

from bot.text import build_stepper, format_uah, mask_contact, mask_name, normalize_code


class NormalizeCode(unittest.TestCase):
    def test_accepts_common_spellings(self):
        for raw in ("MTL-7K2QPX", "mtl-7k2qpx", "MTL 7K2QPX", "7k2qpx", " mtl_7k2qpx "):
            self.assertEqual(normalize_code(raw), "MTL-7K2QPX", raw)

    def test_rejects_non_codes(self):
        for raw in (None, "", "hello there", "<b>", "MTL-", "MTL-AB", "MTL-ABCDEFGHIJK", "MTL-ÄBC123"):
            self.assertIsNone(normalize_code(raw), raw)


class Masks(unittest.TestCase):
    def test_contact(self):
        self.assertEqual(mask_contact("@nikita_sl"), "@nik***")
        self.assertEqual(mask_contact("+380671234567"), "+380*****4567")
        self.assertEqual(mask_contact(None), "—")

    def test_name(self):
        self.assertEqual(mask_name("Nikita Slieptsov"), "Nikita S.")
        self.assertEqual(mask_name("Nikita"), "Nikita")
        self.assertEqual(mask_name("  "), "N/A")


class Stepper(unittest.TestCase):
    def test_marks_steps(self):
        out = build_stepper(["A", "B", "C"], 1).splitlines()
        self.assertEqual(out, ["■ <s>A</s>", "▸ <b>B</b>", "□ C"])


class Money(unittest.TestCase):
    def test_format(self):
        self.assertEqual(format_uah(7299), "7,299 UAH")
        self.assertEqual(format_uah(None), "— UAH")


if __name__ == "__main__":
    unittest.main()
