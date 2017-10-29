from sqlalchemy import (Table, Column,
                        Date, DateTime, Float, Index, Integer, String, Text, Boolean,
                        ForeignKey, ForeignKeyConstraint,
                        select, join, outerjoin, text, func, between, extract, case,
                        and_, or_)
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

import sqlahelper
from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
metadata = Base.metadata



class Users(Base):
    """Model for the stations users"""
    __tablename__ = 'rdvchiro.users'

    id = Column(Integer, primary_key = True)
    first_name = Column(String(256))
    last_name = Column(String(256))
    phone_number = Column(String(256))
    email = Column(String(256))
