from datetime import date
import unittest

from quant_engine import (
    SymbolFactorSnapshot,
    calculate_factor_scores,
    calculate_final_score,
    clamp_score,
    is_recommendation_in_cooldown,
    map_rating,
    normalize_metric,
    sector_relative_percentiles,
    strong_buy_streak,
)


class TestFactorFunctions(unittest.TestCase):
    def test_clamp_score(self) -> None:
        self.assertEqual(clamp_score(-10), 0.0)
        self.assertEqual(clamp_score(120), 100.0)
        self.assertEqual(clamp_score(42.5), 42.5)

    def test_normalize_metric(self) -> None:
        self.assertEqual(normalize_metric(15, 10, 20), 50.0)
        self.assertEqual(normalize_metric(15, 10, 20, inverse=True), 50.0)
        self.assertEqual(normalize_metric(0, 1, 1), 50.0)

    def test_calculate_factor_scores(self) -> None:
        scores = calculate_factor_scores(
            {
                'pe_ratio': 12,
                'pb_ratio': 1.5,
                'revenue_growth_yoy': 0.22,
                'eps_growth_yoy': 0.3,
                'gross_margin': 0.48,
                'roe': 0.18,
                'roa': 0.08,
                'return_3m': 0.12,
                'return_6m': 0.2,
                'eps_revision_3m': 0.05,
                'analyst_target_spread': 0.1,
            }
        )
        self.assertEqual(set(scores.keys()), {'value', 'growth', 'profitability', 'momentum', 'expectation'})
        for value in scores.values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 100)

    def test_calculate_final_score(self) -> None:
        score = calculate_final_score({'value': 100, 'growth': 50, 'profitability': 50, 'momentum': 50, 'expectation': 50})
        self.assertAlmostEqual(score, 60.0)

        weighted = calculate_final_score(
            {'value': 90, 'growth': 10, 'profitability': 10, 'momentum': 10, 'expectation': 10},
            weights={'value': 3, 'growth': 1, 'profitability': 1, 'momentum': 1, 'expectation': 1},
        )
        self.assertGreater(weighted, 40)

    def test_map_rating(self) -> None:
        self.assertEqual(map_rating(90), 'Strong Buy')
        self.assertEqual(map_rating(75), 'Buy')
        self.assertEqual(map_rating(55), 'Hold')
        self.assertEqual(map_rating(30), 'Sell')
        self.assertEqual(map_rating(5), 'Strong Sell')

    def test_sector_relative_percentiles(self) -> None:
        snapshots = [
            SymbolFactorSnapshot('AAA', 'Tech', {'value': 90, 'growth': 80, 'profitability': 70, 'momentum': 60, 'expectation': 50}),
            SymbolFactorSnapshot('BBB', 'Tech', {'value': 10, 'growth': 20, 'profitability': 30, 'momentum': 40, 'expectation': 50}),
            SymbolFactorSnapshot('CCC', 'Finance', {'value': 80, 'growth': 70, 'profitability': 60, 'momentum': 50, 'expectation': 40}),
        ]
        ranked = sector_relative_percentiles(snapshots)
        self.assertEqual(len(ranked), 3)
        aaa = next(item for item in ranked if item.symbol == 'AAA')
        bbb = next(item for item in ranked if item.symbol == 'BBB')
        self.assertGreater(aaa.final_score, bbb.final_score)
        self.assertIn(aaa.rating, {'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'})

    def test_strong_buy_streak(self) -> None:
        self.assertEqual(strong_buy_streak(['Buy', 'Strong Buy', 'Strong Buy']), 2)
        self.assertEqual(strong_buy_streak(['Strong Buy', 'Buy', 'Strong Buy']), 1)
        self.assertEqual(strong_buy_streak([]), 0)

    def test_recommendation_cooldown(self) -> None:
        as_of = date(2026, 3, 9)
        self.assertFalse(is_recommendation_in_cooldown(None, as_of, 7))
        self.assertTrue(is_recommendation_in_cooldown(date(2026, 3, 5), as_of, 7))
        self.assertFalse(is_recommendation_in_cooldown(date(2026, 2, 20), as_of, 7))


if __name__ == '__main__':
    unittest.main()
