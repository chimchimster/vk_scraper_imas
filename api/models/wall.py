from typing import Optional, List

from .common import *
from .base import Base


class Wall(Base):
    id: Optional[int]
    owner_id: Optional[int]
    from_id: Optional[int]
    date: Optional[int]
    likes: Optional[PostLikes]
    post_type: Optional[str]
    reposts: Optional[PostReposts]
    text: Optional[str] = ''
    views: Optional[PostViews] = 0
    attachments: Optional[List[PostAttachment]] = None
    copy_history: Optional[List[CopyHistory]] = None
