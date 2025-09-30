from typing import Any, Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    RATING = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: Response) -> Generator[dict | Any]:
        for book in response.css("h3 a::attr(href)").getall():
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator[dict | Any]:
        yield {
            "title": response.css("div.product_main h1::text").get(default=""),
            "price": response.css("p.price_color::text").get(default=""),
            "amount_in_stock": "".join(
                [s for s in response.css("p.instock::text").getall()[1] if s.isdigit()]
            ),
            "rating": self.RATING.get(
                response.css("p.star-rating::attr(class)").get().split()[-1], None
            ),
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "upc": response.css("table.table.table-striped tr td::text").get(
                default=""
            ),
            "description": response.css("#product_description ~ p::text").get(
                default=""
            ),
        }
