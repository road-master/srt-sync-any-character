import pytest

from cut_scene import ConsecutivePeriod, create_list_consecutive_period


@pytest.mark.parametrize(
    ["list_index", "expected"],
    [
        # Single consecutive period
        ([0, 1], [ConsecutivePeriod(0, 1)]),
        # Multiple consecutive periods
        ([0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12], [ConsecutivePeriod(0, 3), ConsecutivePeriod(5, 12)]),
        (
            [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16],
            [ConsecutivePeriod(0, 3), ConsecutivePeriod(5, 12), ConsecutivePeriod(14, 16)],
        ),
        # No consecutive period
        ([0, 2, 4], [ConsecutivePeriod(0, 0), ConsecutivePeriod(2, 2), ConsecutivePeriod(4, 4)]),
        # Empty list
        ([], []),
        # Single element
        ([0], [ConsecutivePeriod(0, 0)]),
    ],
)
def test(list_index: list[int], expected: list[ConsecutivePeriod]) -> None:
    assert list(create_list_consecutive_period(list_index)) == expected
