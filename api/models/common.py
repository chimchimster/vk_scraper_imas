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
    id: Optional[Union[int, None]] = None
    title: Optional[Union[str, None]] = None


class ConnectionsInfo(Base):
    connections: Optional[Union[Dict, None]] = None


class ContactsInfo(Base):
    mobile_phone: Optional[Union[str, None]] = None
    home_phone: Optional[Union[str, None]] = None


class CountersInfo(Base):
    albums: Optional[Union[int, None]] = None
    videos: Optional[Union[int, None]] = None
    audios: Optional[Union[int, None]] = None
    photos: Optional[Union[int, None]] = None
    notes: Optional[Union[int, None]] = None
    friends: Optional[Union[int, None]] = None
    gifts: Optional[Union[int, None]] = None
    groups: Optional[Union[int, None]] = None
    online_friends: Optional[Union[int, None]] = None
    mutual_friends: Optional[Union[int, None]] = None
    user_videos: Optional[Union[int, None]] = None
    user_photos: Optional[Union[int, None]] = None
    followers: Optional[Union[int, None]] = None
    pages: Optional[Union[int, None]] = None
    subscriptions: Optional[Union[int, None]] = None


class CountryInfo(Base):
    id: Optional[Union[int, None]] = None
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
    id: Optional[Union[int, None]] = None
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
    id: Optional[Union[int, None]] = None
    name: Optional[Union[str, None]] = None
    type: Optional[Union[str, None]] = None


class PlaceInfo(Base):
    id: Optional[Union[int, None]] = None
    title: Optional[Union[str, None]] = None
    latitude: Optional[Union[float, None]] = None
    longitude: Optional[Union[float, None]] = None
    type: Optional[Union[str, None]] = None
    country: Optional[Union[int, None]] = None
    city: Optional[Union[int, None]] = None
    address: Optional[Union[str, None]] = None



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
    post_id: Optional[int]
    album_id: Optional[int]
    date: Optional[int]
    text: Optional[str] = ''
    sizes: Optional[List[PhotoUrl]] = None


class AttachmentVideo(Base):
    id: Optional[int]
    owner_id: Optional[int]
    title: Optional[str] = ''
    description: Optional[str] = ''
    date: Optional[int]
    views: Optional[int] = 0
    image: Optional[List[PhotoUrl]] = None


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
    text: Optional[str]
    attachments: Optional[List[Union[AttachmentVideo, AttachmentPhoto, AttachmentAudio]]] = None
