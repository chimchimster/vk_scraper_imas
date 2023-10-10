from typing import Optional, Union, Dict, List

from pydantic import conint

from .base import Base


class CareerInfo(Base):
    group_id: Optional[Union[int, None]] = None
    company: Optional[Union[str, None]] = None
    country_id: Optional[Union[int, None]] = None
    city_id: Optional[Union[int, None]] = None
    city_name: Optional[Union[str, None]] = None
    from_year: Optional[Union[int, None]] = None
    until_year: Optional[Union[int, None]] = None
    position: Optional[Union[str, None]] = None


class CityInfo(Base):
    title: Optional[Union[str, None]] = None


class ConnectionsInfo(Base):
    connections: Optional[Union[Dict, None]] = None


class ContactsInfo(Base):
    mobile_phone: Optional[Union[str, None]] = None
    home_phone: Optional[Union[str, None]] = None


class CountersInfo(Base):
    friends: Optional[Union[int, None]] = None
    followers: Optional[Union[int, None]] = None


class CountryInfo(Base):
    title: Optional[Union[str, None]] = None


class EducationInfo(Base):
    university: Optional[Union[int, None]] = None
    university_name: Optional[Union[str, None]] = None
    faculty: Optional[Union[int, None]] = None
    faculty_name: Optional[Union[str, None]] = None
    graduation: Optional[Union[int, None]] = None


class LastSeenInfo(Base):
    time: Optional[Union[int, None]] = None
    platform: Optional[Union[int, None]] = None


class MilitaryInfo(Base):
    unit: Optional[Union[str, None]] = None
    unit_id: Optional[Union[int, None]] = None
    country_id: Optional[Union[int, None]] = None
    _from: Optional[Union[int, None]] = None
    until: Optional[Union[int, None]] = None


class OccupationInfo(Base):
    type: Optional[Union[str, None]] = None
    name: Optional[Union[str, None]] = None


class PersonalInfo(Base):
    political: Optional[Union[int, None]] = None
    langs: Optional[Union[list, None]] = None
    religion: Optional[Union[str, None]] = None
    inspired_by: Optional[Union[str, None]] = None
    people_main: Optional[Union[int, None]] = None
    life_main: Optional[Union[int, None]] = None
    smoking: Optional[Union[int, None]] = None
    alcohol: Optional[Union[int, None]] = None


class RelativeInfo(Base):
    name: Optional[Union[str, None]] = None
    type: Optional[Union[str, None]] = None


class PostLikes(Base):
    count: Optional[int] = 0


class PostReposts(Base):
    count: Optional[int] = 0


class PostViews(Base):
    count: Optional[int] = 0


class PhotoUrl(Base):
    url: Optional[str]


class AttachmentPhoto(Base):
    id: Optional[int]
    owner_id: Optional[int]
    post_id: Optional[int] = None
    album_id: Optional[int] = None
    date: Optional[int]
    text: Optional[str] = ''
    sizes: Optional[List[PhotoUrl]] = None

    def __init__(self, **data):
        super().__init__(**data)

        if self.sizes:
            self.sizes = [self.sizes[-1]]


class AttachmentVideo(Base):
    id: Optional[int]
    owner_id: Optional[int]
    title: Optional[str] = ''
    description: Optional[str] = ''
    date: Optional[int]
    views: Optional[int] = 0
    image: Optional[List[PhotoUrl]] = None

    def __init__(self, **data):
        super().__init__(**data)

        if self.image:
            self.image = [self.image[-1]]


class Audio(Base):
    id: Optional[int]
    owner_id: Optional[int]
    title: Optional[str] = ''
    artist: Optional[str] = ''
    url: Optional[str] = ''
    date: Optional[int]


class AttachmentAudio(Base):
    type: Optional[str] = ''
    audio: Optional[Audio] = None


class PostAttachment(Base):
    type: Optional[str] = ''
    photo: Optional[AttachmentPhoto] = None
    video: Optional[AttachmentVideo] = None
    audio: Optional[AttachmentAudio] = None


class CopyHistory(Base):
    id: Optional[int]
    owner_id: Optional[int]
    from_id: Optional[int]
    type: Optional[str]
    text: Optional[str] = ''
    attachments: Optional[List[Union[AttachmentVideo, AttachmentPhoto, AttachmentAudio]]] = None


__all__ = [
    'CopyHistory',
    'PostAttachment',
    'Audio',
    'AttachmentVideo',
    'AttachmentPhoto',
    'PhotoUrl',
    'PostViews',
    'PostReposts',
    'PostLikes',
    'CountryInfo',
    'CareerInfo',
    'CityInfo',
    'ConnectionsInfo',
    'ContactsInfo',
    'CountersInfo',
    'RelativeInfo',
    'PersonalInfo',
    'OccupationInfo',
    'MilitaryInfo',
    'LastSeenInfo',
    'EducationInfo',
]
