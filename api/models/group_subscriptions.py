from typing import Optional, Union, List

from .base import Base
from .common import CityInfo, CountryInfo


class SubscribedToGroup(Base):
    id: int  # source_id
    name: Optional[str] = None
    is_closed: Optional[Union[int, None]] = None
    deactivated: Optional[Union[str, None]] = None
    photo_200: Optional[Union[str, None]] = None
    activity: Optional[Union[str, None]] = None
    age_limits: Optional[Union[int, None]] = None
    city: Optional[Union[CityInfo, List]] = None
    country: Optional[Union[CountryInfo, List]] = None
    description: Optional[Union[str, None]] = None
    members_count: Optional[Union[int, None]] = None
    site: Optional[Union[str, None]] = None
    status: Optional[Union[str, None]] = None
    type: Optional[Union[str, None]] = None

