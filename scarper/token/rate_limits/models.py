import time
from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, Text, DateTime, Boolean, Column, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Text, nullable=False)

    state = relationship('State', back_populates='tokens')

    __table_args__ = (
        UniqueConstraint('token', name='uq_token'),
    )


class VKObject(Base):
    __tablename__ = 'vk_object'

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_name = Column(String(length=255), nullable=False)
    rate_limit = Column(Integer, default=0)

    state = relationship('State', back_populates='vk_object')

    __table_args__ = (
        UniqueConstraint('object_name', name='uq_object_name'),
    )


class State(Base):
    __tablename__ = 'state'

    id = Column(Integer, primary_key=True, autoincrement=True)

    expired = Column(Boolean, default=False)
    expired_at_unix = Column(BigInteger)
    last_use_unix = Column(BigInteger, default=time.time())

    requests = Column(Integer, default=0)

    token_id = Column(Integer, ForeignKey('tokens.id'))
    tokens = relationship('Token', back_populates='state')

    vk_object_id = Column(Integer, ForeignKey('vk_object.id'))
    vk_object = relationship('VKObject', back_populates='state')

    __table_args__ = (
        UniqueConstraint('token_id', 'vk_object_id', name='uq_token_vkobject'),
    )
