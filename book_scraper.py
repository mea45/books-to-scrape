#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To use this script, run the following code:
    
    -------------------------------------
    from book_scraper import book_scraper
    
    Categories, Catalog = book_scraper(t)
    -------------------------------------

If you leave t empty, it will be set to default (t=1.5 seconds).
    
"""

import numpy as np
import pandas as pd
import re
import requests
import time
from bs4 import BeautifulSoup

# function that returns the HTML page through BeautifulSoup
def scraper(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

# function that builds the dataframes Categories and Catalog
def book_scraper(t=1.5):
    # check whether t has an appropriate value
    if not (isinstance(t, (float, int)) or t is None):
        print('Make sure to enter a numerical value for t, or leave it empty.')
        return
    
    ##########################################################################
    #####           GATHER INFORMATION FOR EACH BOOK CATEGORY            #####
    ##########################################################################
    
    # scrape home page
    url = 'http://books.toscrape.com'
    soup = scraper(url)
    
    # extract list of book categories
    text_to_select = 'catalogue/category/books/'
    all_a = soup.find_all('a')
    cat_name = [text.string.strip() for text in all_a if text_to_select in text.get('href')]
    cat_urlcode = [text.get('href').split('/books/')[1].split('/')[0] for text in all_a if text_to_select in text.get('href')]
    
    # create dataframe to store category information
    Categories = pd.DataFrame({
        'Name': cat_name,
        'URL': cat_urlcode
    })
    
    # counting number of books per category
    cat_size = []

    for i in range(Categories.shape[0]):
        url = f'http://books.toscrape.com/catalogue/category/books/{Categories.URL[i]}/index.html'
        cat_size.append(scraper(url).find_all('strong')[1].text)
        
    # add category size and number of pages per category to the dataframe Categories
    Categories['Size'] = cat_size
    Categories['Size'] = Categories['Size'].astype('int64')
    Categories['Pages'] = np.ceil(Categories['Size']/20).astype('int64')
    
    ##########################################################################
    #####           GATHER INFORMATION FOR EACH INDIVIDUAL BOOK          #####
    ##########################################################################
    
    # initialize lists (these will be added to in the loop below using the function .extend())
    title = []
    stars = []
    price = []
    in_stock = []
    book_url = []
    category = []
    
    # loop through all categories
    for i in range(Categories.shape[0]):
        # extract title, star rating, price and stock information from the index page (notice that URL is not yet included here, see below why)
        url = f'http://books.toscrape.com/catalogue/category/books/{Categories.URL[i]}/index.html'
        soup = scraper(url)
        title.extend([text.get('alt') for text in soup.find_all('img')])
        stars.extend([soup.find_all('p')[i].get('class')[1] for i in range(0, len(soup.find_all('p')), 3)])
        price.extend([soup.find_all('p')[i].text.strip() for i in range(1, len(soup.find_all('p')), 3)])
        in_stock.extend([soup.find_all('p')[i].text.strip() for i in range(2, len(soup.find_all('p')), 3)])
    
        # categories that have more than one page have different looking pages since they have the option to go to the next/previous page at the bottom
        # which adds elements to the list resulting from << soup.find_all('a') >>. this is dealt with uing if/else statements
        if Categories.Pages[i] > 1: # category in loop has more than one page
            # 1 element is added to list resulting from << soup.find_all('a') >>: next button
            # also, notice that we start the iteration at the 43rd element. that's because all the elements before are other parts of the page
            book_url.extend([f"http://books.toscrape.com/catalogue{url.get('href').rsplit('..', 1)[1]}" for url in soup.find_all('a')[54:-1:2]])
    
            # loop through pages 2 and up
            for p in range(1, Categories.Pages[i]):
                # extract title, star rating, price and stock information from the index page
                url = f'http://books.toscrape.com/catalogue/category/books/{Categories.URL[i]}/page-{p+1}.html'
                soup = scraper(url)
                title.extend([text.get('alt') for text in soup.find_all('img')])
                stars.extend([soup.find_all('p')[i].get('class')[1] for i in range(0, len(soup.find_all('p')), 3)])
                price.extend([soup.find_all('p')[i].text.strip() for i in range(1, len(soup.find_all('p')), 3)])
                in_stock.extend([soup.find_all('p')[i].text.strip() for i in range(2, len(soup.find_all('p')), 3)])
    
                # again, categories that have more than two pages, have different looking middle pages (so different from the first and last page)
                if p == Categories.Pages[i]: # page in the loop is the final page 
                                             # (1 element is added to list resulting from << soup.find_all('a') >>: previous button)
                    book_url.extend([f"http://books.toscrape.com/catalogue{url.get('href').rsplit('..', 1)[1]}" for url in soup.find_all('a')[54:-1:2]])
                else: # page in the loop is a middle page (2 elements are added to list resulting from << soup.find_all('a') >>: previous and next button)
                    book_url.extend([f"http://books.toscrape.com/catalogue{url.get('href').rsplit('..', 1)[1]}" for url in soup.find_all('a')[54:-2:2]])
        else: # category in loop only has one page (the index page)
            book_url.extend([f"http://books.toscrape.com/catalogue{url.get('href').rsplit('..', 1)[1]}" for url in soup.find_all('a')[54::2]])
    
        # add category corresponding to the book
        category.extend([Categories.Name[i]] * Categories.Size[i])
        
        # being friendly to the server
        time.sleep(t)
        
    # create dataframe to store category information
    Catalog = pd.DataFrame({
        'Title': title,
        'Stars': stars,
        'Price': price,
        'In_Stock': in_stock,
        'URL': book_url,
        'Category': category
    })
    
    # cleaning up the data
    Catalog['Price'] = [price[2:] for price in Catalog.Price]
    Catalog = Catalog.astype({'Price':'float'})
    
    nmbrs = ['One', 'Two', 'Three', 'Four', 'Five']
    
    for i in range(5):
        Catalog.loc[Catalog['Stars'] == nmbrs[i], 'Stars'] = i + 1
    
    Catalog = Catalog.astype({'Stars':'int64'})
    
    # initialize lists (these will be added to in the loop below using the function .extend())
    stock = []
    description = []
    upc = []
    
    # loop through all the books
    for url in book_url:
        soup = scraper(url)
        stock.append(re.findall(r'\d+', soup.find('p', class_='instock availability').text)[0])
        description.append(soup.find('meta', attrs={'name': 'description'}).get('content'))
        upc.append(soup.find_all('tr')[0].text[4:-1])
        time.sleep(1.5)
    
    # adding extracted data to the Catalog dataframe
    Catalog['Stock_Size'] = stock
    Catalog['Description'] = description
    Catalog['UPC'] = upc
    Catalog = Catalog.astype({'Stock_Size':'int64'})
    
    # creating unique identifiers for the categories and the books
    Categories['ID'] = range(1, Categories.shape[0] + 1)
    Catalog['ID'] = range(1, Catalog.shape[0] + 1)
    
    Catalog['Category_ID'] = [0] * Catalog.shape[0]
    
    for i in range(Categories.shape[0]):
        Catalog.loc[Catalog['Category'] == Categories.loc[i, 'Name'], 'Category_ID'] = Categories.loc[i, 'ID']

    # rearranging columns
    catcols = list(Categories.columns)
    catcols.remove('ID')
    ['ID'] + catcols
    
    Categories = Categories[['ID'] + catcols]
    
    catcols = list(Catalog.columns)
    catcols.remove('ID')
    ['ID'] + catcols
    
    Catalog = Catalog[['ID'] + catcols]
    
    return Categories, Catalog



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    