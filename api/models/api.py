from typing import Optional, Union

from .base import Base
from .user import VKUser
from .group_subscriptions import SubscribedToGroup
from .user_subscriptions import SubscribedToUser


class ApplicationConnector(Base):
    user: Union[Optional[VKUser], None] = None
    subscribed_to_group: Union[Optional[SubscribedToGroup], None] = None
    subscribed_to_user: Union[Optional[SubscribedToUser], None] = None

