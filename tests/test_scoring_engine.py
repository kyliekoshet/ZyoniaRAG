import unittest
from scoring.scoring_engine import score_property, rank_properties

class TestScoringEngine(unittest.TestCase):
    def setUp(self):
        # Mock properties
        self.properties = [
            {"id": "A", "price": 300000, "size": 80, "amenities": 5},
            {"id": "B", "price": 250000, "size": 70, "amenities": 3},
            {"id": "C", "price": 400000, "size": 100, "amenities": 7},
            {"id": "D", "price": 350000, "size": 90, "amenities": 6},
        ]
        # User weights (higher weight = more important)
        self.weights = {"price": -10, "size": 5, "amenities": 2}  # Negative for price (lower is better)
        self.total_weight = sum(abs(w) for w in self.weights.values())
        self.min_score = (sum(w for w in self.weights.values() if w < 0) / self.total_weight) * 100
        self.max_score = (sum(w for w in self.weights.values() if w > 0) / self.total_weight) * 100

    def test_score_property(self):
        # Compute normalization info
        normalization_info = {
            "price": (250000, 400000),
            "size": (70, 100),
            "amenities": (3, 7)
        }
        prop = self.properties[0]
        score = score_property(prop, self.weights, normalization_info)
        self.assertIsInstance(score, float)
        # Check score is within theoretical min/max
        self.assertGreaterEqual(score, self.min_score)
        self.assertLessEqual(score, self.max_score)

    def test_rank_properties(self):
        ranked = rank_properties(self.properties, self.weights, return_justification=True)
        self.assertEqual(len(ranked), len(self.properties))
        self.assertTrue(all("score" in r for r in ranked))
        # Check descending order
        scores = [r["score"] for r in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

if __name__ == "__main__":
    unittest.main() 