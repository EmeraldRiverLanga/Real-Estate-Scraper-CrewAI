# test_scraper.py

from scraper import clean_price, is_skeleton, parse_listings


def test_clean_price_basic():
    assert clean_price("450 000 €") == 450000


def test_clean_price_with_badge():
    assert clean_price("Jauna cena195 000 €") == 195000


def test_clean_price_million():
    assert clean_price("1 300 000 €") == 1300000


def test_clean_price_no_number():
    assert clean_price("Cena pēc pieprasījuma") is None


def test_is_skeleton_placeholder():
    assert is_skeleton("mmmmm") is True


def test_is_skeleton_real_address():
    assert is_skeleton("Lienes iela 6A") is False


def test_is_skeleton_single_word():
    assert is_skeleton("Miglači") is False


def test_is_skeleton_empty():
    assert is_skeleton("") is True


def test_parse_listings_extracts_fields():
    html = """
    <div class="object object--list object--result">
      <a href="/real-estate/commercials-for-sale/test/123" class="object__attributes">
        <div class="object__address">Test iela 1</div>
        <div class="object__area">Rīga</div>
        <div class="object__purpose">Birojs</div>
      </a>
      <div class="object-price__main-price">100 000 €</div>
    </div>
    """
    result = parse_listings(html)
    assert len(result) == 1
    row = result[0]
    assert row["address"] == "Test iela 1"
    assert row["city"] == "Rīga"
    assert row["category"] == "Birojs"
    assert row["price_eur"] == 100000
    assert row["link"] == "https://www.city24.lv/real-estate/commercials-for-sale/test/123"


def test_parse_listings_skips_skeleton():
    html = '<div class="object--result"><div class="object__address">mmmmm</div></div>'
    assert parse_listings(html) == []