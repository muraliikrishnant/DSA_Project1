import unittest

from bloom_filter import BloomFilter
from heap_topk import top_k
from mergesort import mergesort
from quicksort import quicksort_in_place


class TestSorting(unittest.TestCase):
    def test_quicksort_matches_baseline(self) -> None:
        items = [(3, 2), (1, 2), (2, 3), (9, 1), (8, 1), (7, 1)]
        expected = sorted(items, key=lambda t: (-t[1], t[0]))
        data = items.copy()
        quicksort_in_place(data, seed=123)
        self.assertEqual(data, expected)

    def test_mergesort_matches_baseline(self) -> None:
        items = [(3, 2), (1, 2), (2, 3), (9, 1), (8, 1), (7, 1)]
        expected = sorted(items, key=lambda t: (-t[1], t[0]))
        self.assertEqual(mergesort(items), expected)


class TestTopK(unittest.TestCase):
    def test_topk_basic(self) -> None:
        items = [(10, 5), (1, 5), (7, 2), (3, 9), (2, 1)]
        expected = sorted(items, key=lambda t: (-t[1], t[0]))[:3]
        self.assertEqual(top_k(items, 3), expected)

    def test_topk_k_gt_n(self) -> None:
        items = [(1, 1), (2, 2)]
        expected = sorted(items, key=lambda t: (-t[1], t[0]))
        self.assertEqual(top_k(items, 10), expected)

    def test_topk_k_zero(self) -> None:
        self.assertEqual(top_k([(1, 1)], 0), [])


class TestBloom(unittest.TestCase):
    def test_bloom_no_false_negatives(self) -> None:
        bf = BloomFilter(m_bits=10_000, k_hashes=5)
        items = [f"ip-{i}" for i in range(1000)]
        for s in items:
            bf.add(s)
        for s in items:
            self.assertIn(s, bf)


if __name__ == "__main__":
    unittest.main()

