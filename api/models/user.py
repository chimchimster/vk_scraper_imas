from typing import Optional, List, Union, Dict

from .common import *

from .base import Base


class VKUser(Base):
    id: int
    first_name: str
    last_name: str
    deactivated: Optional[Union[str, None]] = None
    is_closed: Optional[Union[bool, None]] = None
    about: Optional[Union[str, None]] = None
    activities: Optional[Union[str, None]] = None
    bdate: Optional[Union[str, None]] = None
    career: Optional[List[CareerInfo]] = None
    city: Optional[Union[CityInfo, List[CityInfo]]] = None
    connections: Optional[Union[ConnectionsInfo, List]] = None
    contacts: Optional[Union[ContactsInfo, List]] = None
    counters: Optional[Union[CountersInfo, List]] = None  # friends, followers
    country: Optional[Union[CountryInfo, List]] = None
    education: Optional[Union[EducationInfo, List]] = None
    home_town: Optional[Union[str, None]] = None
    interests: Optional[Union[str, None]] = None
    last_seen: Optional[Union[LastSeenInfo, List]] = None  # в отдельную таблицу
    military: Optional[Union[MilitaryInfo, List]] = None
    movies: Optional[Union[str, None]] = None
    music: Optional[Union[str, None]] = None
    occupation: Optional[Union[OccupationInfo, List]] = None
    personal: Optional[Union[PersonalInfo, List]] = None
    photo_max_orig: Optional[Union[str, None]] = None
    quotes: Optional[Union[str, None]] = None
    relatives: Optional[Union[RelativeInfo, List]] = None
    relation: Optional[Union[int, None]] = None
    sex: Optional[Union[int, None]] = None
    site: Optional[Union[str, None]] = None
    status: Optional[Union[str, None]] = None

