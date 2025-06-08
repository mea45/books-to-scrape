# First Web Scraping Project: Scraping Book Data from a Webshop

## Introduction
For this beginner web scraping project, we gratefully made use of the website, http://books.toscrape.com, which is created and published for the main purpose to be scraped. It is a mock book webshop containing 1000 books spread over 50 different categories. 

## Script
In the [Jupyter Notebook](https://github.com/manalelabdellaoui/books-to-scrape/blob/main/web_scraping.ipynb) all the steps that are made to scrape the website and to create the datasets are found. To run the code, you can also use the [Python script](https://github.com/manalelabdellaoui/books-to-scrape/blob/main/book_scraper.py). To use the script, run the following code:

```python 
from book_scraper import book_scraper
    
Categories, Catalog = book_scraper(t)
```

`t` is the time out length in seconds to deal with rate limiting. If you leave it empty, it will be set to default (`t = 1.5` seconds).

This script depends on the following packages:
- `numpy`
- `pandas`
- `re`
- `requests`
- `time`
- `BeautifulSoup` (from `bs4`)

If you just want to obtain the datasets without running the script yourself, you can click on the links found below.

## Datasets
The script returns two dataframes: [`Categories`](https://github.com/manalelabdellaoui/books-to-scrape/blob/main/Categories.csv) and [`Catalog`](https://github.com/manalelabdellaoui/books-to-scrape/blob/main/Catalog.csv). 

`Categories` contains information gathered on each of the book categories:
- `ID`: unique identifier for each category;
- `Name`: name of the category (e.g., Travel, Mystery, Historical Fiction etc.);
- `URL`: URL of the category's index page;
- `Size`: number of titles in the category;
- `Pages`: number of web pages for the category.

`Catalog` contains information gathered on each individual book:
- `ID`: unique identifier for each individual book;
- `Title`: title of the book;
- `Stars`: star rating (1-5);
- `Price`: price for which the book is sold;
- `In_Stock`: binary stock availability;
- `URL`: URL of the individual book's page;
- `Category`: category to which the book belongs;
- `Stock_Size`: number of copies of the book available;
- `Description`: description of the book's content;
- `UPC`: Universal Product Code;
- `Category_ID`: unique identifier of the category to which the book belongs.
