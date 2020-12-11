# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst
import re
# Importing the required libraries
import contextlib
from urllib.parse import urlencode
import sys
from urllib.request import urlopen
import gdshortener
# Defining the function to shorten a URL

s = gdshortener.ISGDShortener()


def make_shorten(url):
    return s.shorten(url)


DOMAIN = "https://www.booking.com"


def parseDistance(text):
    return text


def parseFloatNumber(text):
    txt = text.strip()
    txt = txt.replace(",", ".")
    return float(txt)


def parseIntNumber(text):
    txt = text.strip()
    return int(txt)


def parseLinkHotel(text):
    link = "{}/{}".format(DOMAIN, text)
    print("link: ", link)
    short_link = make_shorten(link)
    return short_link


def parsePrice(text):
    txt = re.sub('[^0-9]', '', text)
    txt = parseIntNumber(txt)
    return txt


def parseNumberPeopleRating(text):
    text = text.strip()
    txt = re.sub('[^0-9]', '', text)
    txt = parseIntNumber(txt)
    return txt


def parseImage(link):
    short_link = make_shorten(link)
    return short_link


def parseQualityStar(text):
    if len(text) == 1:
        return int(text)
    else:

        txts = text.split(" ")
        return int(txts[0])


class HotelCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pre-processing after get value text
    hotel_name = Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    hotel_id = Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    address = Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    link = Field(input_processor=MapCompose(
        parseLinkHotel), output_processor=TakeFirst())
    quality_star = Field(input_processor=MapCompose(
        parseQualityStar), output_processor=TakeFirst())
    rating = Field(input_processor=MapCompose(
        parseFloatNumber), output_processor=TakeFirst())
    number_people_rating = Field(input_processor=MapCompose(
        parseNumberPeopleRating), output_processor=TakeFirst())
    description = Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    distance = Field(input_processor=MapCompose(
        parseDistance), output_processor=TakeFirst())
    image = Field(input_processor=MapCompose(
        parseImage), output_processor=TakeFirst())
    price = Field(input_processor=MapCompose(
        parsePrice), output_processor=TakeFirst())
    city_id = Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    pass


class TourItem(scrapy.Item):
    pass
