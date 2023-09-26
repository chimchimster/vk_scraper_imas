from typing import Optional, List, Union

from .common import CareerInfo, CityInfo, ConnectionsInfo, CountryInfo, ContactsInfo, CountersInfo, EducationInfo, \
    PersonalInfo, LastSeenInfo, MilitaryInfo, OccupationInfo, RelativeInfo

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
    books: Optional[Union[str, None]] = None
    career: Optional[Union[CareerInfo, List]] = None
    city: Optional[Union[CityInfo, List[CityInfo]]] = None
    connections: Optional[Union[ConnectionsInfo, List]]
    contacts: Optional[Union[ContactsInfo, List]] = None
    counters: Optional[Union[CountersInfo, List]] = None
    country: Optional[Union[CountryInfo, List]] = None
    crop_photo: Optional[Union[dict, None]] = None
    domain: Optional[Union[str, None]] = None
    education: Optional[Union[EducationInfo, List]] = None
    followers_count: Optional[Union[int, None]] = None
    games: Optional[Union[str, None]] = None
    has_mobile: Optional[Union[int, None]] = None
    has_photo: Optional[Union[int, None]] = None
    home_town: Optional[Union[str, None]] = None
    interests: Optional[Union[str, None]] = None
    last_seen: Optional[Union[LastSeenInfo, List]] = None
    military: Optional[Union[MilitaryInfo, List]] = None
    movies: Optional[Union[str, None]] = None
    music: Optional[Union[str, None]] = None
    nickname: Optional[Union[str, None]] = None
    occupation: Optional[Union[OccupationInfo, List]] = None
    online: Optional[Union[int, None]] = None
    personal: Optional[Union[PersonalInfo, List]] = None
    photo_id: Optional[Union[str, None]] = None
    photo_max_orig: Optional[Union[str, None]] = None
    quotes: Optional[Union[str, None]] = None
    relatives: Optional[Union[RelativeInfo, List]] = None
    relation: Optional[Union[int, None]] = None
    screen_name: Optional[Union[str, None]] = None
    sex: Optional[Union[int, None]] = None
    site: Optional[Union[str, None]] = None
    status: Optional[Union[str, None]] = None
