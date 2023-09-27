from typing import Optional, List, Dict, Union
from .base import Base
from .user import VKUser
from .group_subscriptions import SubscribedToGroup
from .user_subscriptions import SubscribedToUser


class ResponseModel(Base):
    count: Optional[int] = None
    response: Optional[List[Union[VKUser, SubscribedToUser, SubscribedToGroup, List, Dict]]] = None
    items: Optional[Union[VKUser, SubscribedToUser, SubscribedToGroup, List]] = None

