import unittest

from app.services import baby_name_reveal as reveal


class TestBabyNameReveal(unittest.TestCase):
    def test_exact_text_contract(self):
        self.assertEqual(reveal.FATHER, "NITISH")
        self.assertEqual(reveal.MOTHER, "SNEHANKITHA")
        self.assertEqual(reveal.TODDLER, "ITIKA")
        self.assertEqual(
            reveal.PAIRINGS,
            (("N", "SNE"), ("S", "HAN"), ("H", "ITH")),
        )

    def test_output_contract(self):
        self.assertEqual((reveal.WIDTH, reveal.HEIGHT), (1920, 1080))
        self.assertGreaterEqual(reveal.DURATION, 8)
        self.assertLessEqual(reveal.DURATION, 10)

    def test_key_frames_render_at_full_hd(self):
        for t in (0.5, 2.5, 4.0, 5.5, 7.5, 9.0):
            with self.subTest(t=t):
                frame = reveal.make_frame(t)
                self.assertEqual(frame.shape, (1080, 1920, 3))


if __name__ == "__main__":
    unittest.main()
