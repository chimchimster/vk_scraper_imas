from pydantic import Json
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


BaseModel = declarative_base()


class Source(BaseModel):

    __tablename__ = 'source'

    system_id = Column(Integer, primary_key=True)
    soc_type = Column(Integer)
    source_id = Column(Integer)
    source_type = Column(Integer)

    user_profile = relationship('UserProfile', back_populates='source')
    user_subscriptions = relationship('SubscriptionProfile', back_populates='source')


class UserProfile(BaseModel):

    __tablename__ = 'user_profile'

    system_id = Column(Integer, primary_key=True)
    user_name = Column(String(length=255))
    user_surname = Column(String(length=255))
    contacts = Column(String(length=255))
    social_status = Column(Integer)
    profile_image = Column(Text)
    info_json = Column(Json)
    alerts = Column(String(length=255))

    source = relationship('Source', back_populates='user_profile')


class SubscriptionProfile(BaseModel):

    __tablename__ = 'subscription_profile'

    system_id = Column(Integer, primary_key=True)
    subscription_name = Column(String(length=255))
    description = Column(Text)
    profile_image = Column(Text)
    alerts = Column(String(length=255))

    source = relationship('Source', back_populates='subscription_profile')


class UserSubscription(BaseModel):

    __tablename__ = 'user_subscription'

    user_system_id = Column(Integer, ForeignKey('user_profile.system_id'))
    subscription_system_id = Column(Integer, ForeignKey('subscription_profile.system_id'))