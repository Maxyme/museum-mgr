"""Data fetcher tests."""

from data_science.data_science import _parse_number_with_string_multiplier


def test_parse_number_with_string_multiplier():
    """Test parsing numbers with special chars ans string multipliers."""
    numb_response = [
        ("1234 [1]", 1234),
        ("1234 (approx)", 1234),
        ("45,678", 45678),
        ("1 million", 1_000_000),
        ("2.5 million", 2_500_000),
        ("3 million (estimated)", 3_000_000),
    ]
    for text, expected in numb_response:
        assert _parse_number_with_string_multiplier(text) == expected
