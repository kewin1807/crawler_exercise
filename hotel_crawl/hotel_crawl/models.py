from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Hotel(Base):
    __tablename__ = "hotel"
    id = Column(Integer, primary_key=True)
    hotel_name = Column('name', String(50))
    hotel_id = Column("hotel_id", String(50))
    address = Column('address', String(150))
    link = Column("link_hotel", String(1000))
    city_id = Column('city_id', String(150))
    quality_star = Column("quality", Integer)
    rating = Column("rating", Float)
    number_people_rating = Column("number_people_rating", Integer)
    description = Column("description", String(255))
    distance = Column("distance", String(50))
    image = Column("image", String(150))
    price = Column("price", Integer)


class Tour(Base):
    __tablename__ = "tour"
    id = Column(Integer, primary_key=True)
