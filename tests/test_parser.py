import pytest

from sreality_stat.parser import parse_place, get_coords_price_meters


@pytest.mark.parametrize("test_input,expected", [
    ((50.08517074933277, 14.33584785113113), ('Mahulenina', 'Hlavní město Praha', None, None, 15200)),
    ((49.7163253, 16.2656497), ('Tyršova', 'Polička', 'okres Svitavy', 'Pardubický kraj', 57201)),
    ((49.6907228, 16.2267744), (None, "Sádek", 'okres Svitavy', 'Pardubický kraj', 57201)),
    ((49.2070850, 16.6258744), ('Tišnovská', 'Brno', 'okres Brno-město', 'Jihomoravský kraj', 61300))])
def test_parse_place(test_input, expected):
    result = parse_place(test_input)
    assert result == expected


def test_get_coords_price_meters():
    result = get_coords_price_meters('2834848604')
    assert result == ()
