import unittest

from models import ConflictType, UrgencyLevel
from pipeline import _normalize_conflict_type, _normalize_urgency


class PipelineNormalizationTests(unittest.TestCase):
    def test_conflict_type_normalization_cases(self):
        cases = [
            ("bullying", ConflictType.BULLYING),
            ("verbal harassment", ConflictType.VERBAL),
            ("social-exclusion", ConflictType.SOCIAL),
            ("cyber bullying", ConflictType.CYBERBULLYING),
            ("weapon", ConflictType.WEAPONS),
            ("fight", ConflictType.PHYSICAL),
            ("physical fight", ConflictType.PHYSICAL),
            ("stalking", ConflictType.THREAT),
            ("stalking|verbal_harassment", ConflictType.THREAT),
            ("fight/harassment", ConflictType.PHYSICAL),
            ("unknown_new_label", ConflictType.OTHER),
            ("", ConflictType.OTHER),
            (None, ConflictType.OTHER),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(_normalize_conflict_type(raw), expected)

    def test_urgency_normalization_cases(self):
        cases = [
            ("low", UrgencyLevel.LOW),
            ("medium", UrgencyLevel.MEDIUM),
            ("high", UrgencyLevel.HIGH),
            ("critical", UrgencyLevel.CRITICAL),
            ("urgent", UrgencyLevel.HIGH),
            ("very urgent", UrgencyLevel.CRITICAL),
            ("immediate", UrgencyLevel.CRITICAL),
            ("unknown_level", UrgencyLevel.MEDIUM),
            ("", UrgencyLevel.MEDIUM),
            (None, UrgencyLevel.MEDIUM),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(_normalize_urgency(raw), expected)


if __name__ == "__main__":
    unittest.main()
