from typing import Optional, Union, List

from .base import Base
from .common import CityInfo, CountryInfo, PlaceInfo


class SubscribedToGroup(Base):
    id: int
    name: str
    screen_name: Optional[Union[str, None]] = None
    is_closed: Optional[Union[int, None]] = None
    deactivated: Optional[Union[str, None]] = None
    type: Optional[Union[str, None]] = None
    photo_200: Optional[Union[str, None]] = None
    activity: Optional[Union[str, None]] = None
    age_limits: Optional[Union[int, None]] = None
    city: Optional[Union[CityInfo, List]] = None
    country: Optional[Union[CountryInfo, List]] = None
    description: Optional[Union[str, None]] = None
    is_favorite: Optional[Union[int, None]] = None
    member_status: Optional[Union[int, None]] = None
    members_count: Optional[Union[int, None]] = None
    site: Optional[Union[str, None]] = None
    place: Optional[Union[PlaceInfo, List]] = None
    status: Optional[Union[str, None]] = None
    verified: Optional[Union[int, None]] = None
    wall: Optional[Union[int, None]] = None
    wiki_page: Optional[Union[str, None]] = None


