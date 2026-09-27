import unittest

from app.services import baby_name_reveal as reveal


class TestBabyNameReveal(unittest.TestCase):
    def test_story_contract(self):
        self.assertEqual(reveal.FATHER, "NITISH")
        self.assertEqual(reveal.MOTHER, "SNEHANKITHA")
        self.assertEqual(reveal.TODDLER, "ITIKA")
        self.assertEqual(reveal.PAIRINGS, (("N", "SNE"), ("S", "HAN"), ("H", "ITH")))
        self.assertEqual(reveal.FATHER_REMAINDER, "ITI")
        self.assertEqual(reveal.MOTHER_REMAINDER, "KA")
        self.assertEqual(reveal.FATHER_REMAINDER + reveal.MOTHER_REMAINDER, reveal.TODDLER)
        self.assertEqual(
            reveal.STAGES,
            (
                ("N", "SNE", "ITISH", "HANKITHA"),
                ("S", "HAN", "ITIH", "KITHA"),
                ("H", "ITH", "ITI", "KA"),
            ),
        )

    def test_exact_removal_indices(self):
        mother = reveal.MOTHER
        self.assertEqual("".join(mother[i] for i in (0, 1, 2)), "SNE")
        self.assertEqual("".join(mother[i] for i in (3, 4, 5)), "HAN")
        self.assertEqual("".join(mother[i] for i in (7, 8, 9)), "ITH")
        removed = {0, 1, 2, 3, 4, 5, 7, 8, 9}
        self.assertEqual("".join(ch for i, ch in enumerate(mother) if i not in removed), "KA")

    def test_output_contract(self):
        self.assertEqual((reveal.WIDTH, reveal.HEIGHT), (1920, 1080))
        self.assertEqual(reveal.FPS, 30)
        self.assertEqual(reveal.DURATION, 10.0)

    def test_representative_frames(self):
        for t in (0.5, 2.5, 3.9, 5.3, 6.6, 7.5, 8.5, 9.7):
            with self.subTest(t=t):
                frame = reveal.make_frame(t)
                self.assertEqual(frame.shape, (1080, 1920, 3))
                self.assertEqual(frame.dtype.name, "uint8")


if __name__ == "__main__":
    unittest.main()
