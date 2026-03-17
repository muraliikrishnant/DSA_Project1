import unittest

from bloom_filter import BloomFilter
from data_generator import generate_uniform_keys, generate_zipf_keys
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


class TestSyntheticGenerator(unittest.TestCase):
    def test_uniform_length_and_pool(self) -> None:
        keys = list(generate_uniform_keys(100, num_ips=10, seed=1))
        self.assertEqual(len(keys), 100)
        self.assertLessEqual(len(set(keys)), 10)

    def test_zipf_length_and_pool(self) -> None:
        keys = list(generate_zipf_keys(200, num_ips=20, alpha=1.2, seed=2))
        self.assertEqual(len(keys), 200)
        self.assertLessEqual(len(set(keys)), 20)


if __name__ == "__main__":
    unittest.main()
