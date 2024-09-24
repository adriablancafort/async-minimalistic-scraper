from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser
import asyncio


async def request_content(session: AsyncSession, URL: str) -> str | None:
    """Request the content of a URL and return it as a string."""

    response = await session.get(URL, impersonate="safari")
    if response.status_code != 200:
        print(f"Error: {response.status_code}, URL: {URL}")
        return None
    return response.text


async def scrape_amazon_product(session: AsyncSession, ASIN: str) -> None:
    """Scrape the price of an Amazon product given its ASIN."""

    URL = f"https://www.amazon.com/dp/{ASIN}"

    html = await request_content(session, URL)

    if html is None:
        return

    tree = HTMLParser(html)

    captcha_title = tree.css_first("h4")
    if captcha_title and "Enter the characters you see below" in captcha_title.text():
        print(f"Error: CAPTCHA, URL: {URL}")
        return

    title_element = tree.css_first("h1 span#productTitle")
    price_symbol_element = tree.css_first("span.a-price-symbol")
    price_whole_element = tree.css_first("span.a-price-whole")
    price_fraction_element = tree.css_first("span.a-price-fraction")

    PRODUCT_TITLE = title_element.text().strip() if title_element else "Title not found"
    PRICE_SYMBOL = price_symbol_element.text() if price_symbol_element else "Symbol not found"
    PRICE_WHOLE = price_whole_element.text().replace(".", "") if price_whole_element else "Whole part not found"
    PRICE_FRACTION = price_fraction_element.text() if price_fraction_element else "Fraction not found"

    print(f"Product Title: {PRODUCT_TITLE}")
    print(f"Price Symbol: {PRICE_SYMBOL}")
    print(f"Price Whole: {PRICE_WHOLE}")
    print(f"Price Fraction: {PRICE_FRACTION}")


async def main():
    ASINs = ["B0BXPFNNF9", "B0D3KPGFHL", "B0B2D77YB8"]
    async with AsyncSession() as session:
        tasks = [scrape_amazon_product(session, ASIN) for ASIN in ASINs]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
