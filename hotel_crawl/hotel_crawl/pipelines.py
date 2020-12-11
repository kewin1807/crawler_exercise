# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from hotel_crawl.models import create_table, db_connect, Hotel
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem


class HotelCrawlPipeline(object):

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        pass

    def process_item(self, item, spider):
        """Save hotels in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        hotel = Hotel()
        hotel.hotel_name = item["hotel_name"]
        hotel.address = item["address"],
        hotel.link = item["link"]
        hotel.quality_star = item["quality_star"]
        hotel.rating = item["rating"]
        hotel.number_people_rating = item["number_people_rating"]
        hotel.description = item["description"]
        hotel.distance = item["distance"]
        hotel.image = item["image"]
        hotel.price = item["price"]
        hotel.city_id = item["city_id"]
        hotel.hotel_id = item["hotel_id"]
        try:
            session.add(hotel)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item


class DuplicatesPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        exist_quote = session.query(Hotel).filter_by(
            hotel_id=item["hotel_id"]).first()
        if exist_quote is not None:  # the current quote exists
            raise DropItem("Duplicate item found: %s" % item["hotel_id"])
            session.close()
        else:
            return item
            session.close()
