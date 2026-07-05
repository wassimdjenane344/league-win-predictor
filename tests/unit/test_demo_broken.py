"""DEMO ONLY: a deliberately failing test to show that CI blocks a broken PR.

This file exists only on the demo/failing-test branch to produce a red X in
GitHub Actions for the presentation. It is never merged.
"""


def test_this_is_broken_on_purpose():
    expected = 100
    actual = 42  # wrong on purpose
    assert actual == expected, "This test fails on purpose to demo the CI blocking a bad PR"
