from sqlalchemy import Column, Integer, SmallInteger, String, Text, Date, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


BaseModel = declarative_base()


class Source(BaseModel):

    __tablename__ = 'source'

    res_id = Column(Integer, primary_key=True, autoincrement=True)
    soc_type = Column(Integer)
    source_id = Column(Integer)
    source_type = Column(Integer)

    user_event = relationship('UserEvent', back_populates='source', uselist=False)
    scrapper_hash = relationship('ScrapperHash', back_populates='source', uselist=False)
    user_profile = relationship('UserProfile', back_populates='source', uselist=False)
    subscription_profile = relationship('SubscriptionProfile', back_populates='source', uselist=False)

    __table_args__ = (
        UniqueConstraint(source_id, name='source_id'),
    )


class UserEvent(BaseModel):

    __tablename__ = 'source_user_event'

    event_time = Column(Integer, primary_key=True)
    event_type = Column(String(length=255), primary_key=True)
    event_value = Column(String(length=255), primary_key=True)

    res_id = Column(Integer, ForeignKey('source.res_id'))
    source = relationship('Source', back_populates='user_event')


class ScrapperHash(BaseModel):

    __tablename__ = 'scrapper_hash'

    res_id = Column(Integer, ForeignKey('source.res_id'), primary_key=True)
    source = relationship('Source', back_populates='scrapper_hash')

    social_info_hash = Column(String(length=255))


class UserProfile(BaseModel):

    __tablename__ = 'source_user_profile'

    res_id = Column(Integer, ForeignKey('source.res_id'), primary_key=True)
    source = relationship('Source', back_populates='user_profile')

    user_name = Column(String(length=255))
    deactivated = Column(Integer)
    is_closed = Column(SmallInteger)
    sex = Column(Integer)
    birthdate = Column(Date)
    profile_image = Column(Text)
    info_json = Column(JSON)
    alerts = Column(String(length=20))


class SubscriptionProfile(BaseModel):

    __tablename__ = 'source_user_subscription'

    res_id = Column(Integer, ForeignKey('source.res_id'), primary_key=True)
    source = relationship('Source', back_populates='subscription_profile')

    subscription_name = Column(String(length=255))
    is_closed = Column(Integer)
    deactivated = Column(Integer)
    members_count = Column(Integer)
    profile_image = Column(Text)
    info_json = Column(JSON)
    alerts = Column(String(length=20))


class UserSubscription(BaseModel):

    __tablename__ = 'user_subscription'

    user_system_id = Column(Integer, ForeignKey('user_profile.system_id'), primary_key=True)
    subscription_system_id = Column(Integer, ForeignKey('subscription_profile.system_id'), primary_key=True)