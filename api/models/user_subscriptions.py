from typing import Dict, List

from base import Base


class CareerInfo(Base):
    group_id: int
    company: str
    country_id: int
    city_id: int
    city_name: str
    from_year: int
    until_year: int
    position: str


class CityInfo(Base):
    id: int
    title: str


class ConnectionsInfo(Base):
    connections: Dict[str, str]


class ContactsInfo(Base):
    mobile_phone: str
    home_phone: str


class CountersInfo(Base):
    albums: int
    videos: int
    audios: int
    photos: int
    notes: int
    friends: int
    gifts: int
    groups: int
    online_friends: int
    mutual_friends: int
    user_videos: int
    user_photos: int
    followers: int
    pages: int
    subscriptions: int


class CountryInfo(Base):
    id: int
    title: str


class EducationInfo(Base):
    university: int
    university_name: str
    faculty: int
    faculty_name: str
    graduation: int


class LastSeenInfo(Base):
    time: int
    platform: int


class MilitaryInfo(Base):
    unit: str
    unit_id: int
    country_id: int
    _from: int
    until: int


class OccupationInfo(Base):
    type: str
    id: int
    name: str


class PersonalInfo(Base):
    political: int
    langs: List[str]
    religion: str
    inspired_by: str
    people_main: int
    life_main: int
    smoking: int
    alcohol: int


class RelativeInfo(Base):
    id: int
    name: str
    type: str


class SubscribedToUser(Base):
    id: int
    first_name: str
    last_name: str
    deactivated: str
    is_closed: bool
    about: str
    activities: str
    bdate: str
    books: str
    career: CareerInfo
    city: CityInfo
    connections: ConnectionsInfo
    contacts: ContactsInfo
    counters: CountersInfo
    country: CountryInfo
    crop_photo: dict
    domain: str
    education: EducationInfo
    followers_count: int
    games: str
    has_mobile: int
    has_photo: int
    home_town: str
    interests: str

    # Дополнительные поля
    last_seen: LastSeenInfo
    military: MilitaryInfo
    movies: str
    music: str
    nickname: str
    occupation: OccupationInfo
    online: int
    personal: PersonalInfo
    photo_id: str
    photo_max_orig: str
    quotes: str
    relatives: RelativeInfo
    relation: int
    screen_name: str
    sex: int
    site: str
    status: str

