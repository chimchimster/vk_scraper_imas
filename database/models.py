from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Text, Date, JSON, ForeignKey, UniqueConstraint, Boolean
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
    last_seen = relationship('LastSeen', back_populates='source', uselist=False)

    __table_args__ = (
        UniqueConstraint(source_id, name='source_id'),
    )


class UserEvent(BaseModel):

    __tablename__ = 'source_user_event'

    event_time = Column(BigInteger, primary_key=True)
    event_type = Column(String(length=255), primary_key=True)
    event_value = Column(Text)

    res_id = Column(Integer, ForeignKey('source.res_id'), primary_key=True, index=True)
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
    birth_date = Column(Date)
    profile_image = Column(Text)
    info_json = Column(JSON)

    user_subscription = relationship('UserSubscription', back_populates='user')


class SubscriptionProfile(BaseModel):

    __tablename__ = 'source_subscription_profile'

    res_id = Column(Integer, ForeignKey('source.res_id'), primary_key=True)
    source = relationship('Source', back_populates='subscription_profile')

    subscription_name = Column(String(length=255))
    is_closed = Column(Integer)
    deactivated = Column(Integer)
    members_count = Column(Integer)
    profile_image = Column(Text)
    info_json = Column(JSON)
    alerts = Column(String(length=20))

    subscription_profile = relationship('UserSubscription', back_populates='subscription')


class UserSubscription(BaseModel):

    __tablename__ = 'source_user_subscription'

    user_res_id = Column(Integer, ForeignKey('source_user_profile.res_id'), primary_key=True)
    subscription_res_id = Column(Integer, ForeignKey('source_subscription_profile.res_id'), primary_key=True)
    status = Column(Boolean)

    user = relationship('UserProfile', back_populates='user_subscription')
    subscription = relationship('SubscriptionProfile', back_populates='subscription_profile')


class LastSeen(BaseModel):

    __tablename__ = 'user_last_seen'

    res_id = Column(Integer, ForeignKey('source.res_id'), primary_key=True)
    time = Column(BigInteger)
    platform = Column(Integer)

    source = relationship('Source', back_populates='last_seen')


__all__ = [
    'Source',
    'UserEvent',
    'ScrapperHash',
    'UserProfile',
    'SubscriptionProfile',
    'UserSubscription',
    'LastSeen',
]
