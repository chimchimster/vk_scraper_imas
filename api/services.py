import asyncio
from config_reader import config
from utils.decorators import do_post_request_to_vk_api

_user_ids = ['id226245594', 'dmitriy_panfilov', 'angieozerova', 'dosia1488', 'favnart', 'aslushnikov']

items = ['activities', 'about', 'blacklisted', 'blacklisted_by_me', 'books', 'bdate', 'can_be_invited_group', 'can_post', 'can_see_all_posts', 'can_see_audio', 'can_send_friend_request', 'can_write_private_message', 'career', 'common_count', 'connections', 'contacts', 'city', 'country', 'crop_photo', 'domain', 'education', 'exports', 'followers_count', 'friend_status', 'has_photo', 'has_mobile', 'home_town', 'photo_100', 'photo_200', 'photo_200_orig', 'photo_400_orig', 'photo_50', 'sex', 'site', 'schools', 'screen_name', 'status', 'verified', 'games', 'interests', 'is_favorite', 'is_friend', 'is_hidden_from_feed', 'last_seen', 'maiden_name', 'military', 'movies', 'music', 'nickname', 'occupation', 'online', 'personal', 'photo_id', 'photo_max', 'photo_max_orig', 'quotes', 'relation', 'relatives', 'timezone', 'tv', 'universities']


class APIAsyncRequests:
    # VK rate limit
    RATE_LIMIT, LATENCY = 3, 1
    API_LINK = 'https://api.vk.com/method/'

    def __init__(self):
        self.__tokens: list[str] = config.vk_token.get_secret_value()

    @property
    def tokens(self) -> list[str]:
        if not self.__tokens:
            return []
        return self.__tokens.split(',')

    @do_post_request_to_vk_api
    async def get_users_info_by_vk_ids(self, user_ids: list, **kwargs) -> str:
        """ Возвращает все возможные поля пользователя VK. """

        fields = kwargs.pop('fields')

        return await self.form_request_string(
            'users.get',
            user_ids=','.join(user_ids),
            fields=','.join(fields),
            access_token=self.tokens[0],
            v=5.131,
        )

    @do_post_request_to_vk_api
    async def get_subscriptions_of_user_by_vk_id(self, user_id: int, **kwargs) -> str:
        """ Возвращает информацию о всех подписках пользователя. """

        return await self.form_request_string(
            'users.getSubscriptions',
            user_id=user_id,
            extended=1,
            access_token=self.tokens[0],
            v=5.131,
        )

    async def form_request_string(self, method: str, **kwargs):

        kwargs = [f'{key}={val}&' for key, val in kwargs.items()]

        return self.API_LINK + """{}?{}""".format(method, ''.join(kwargs)[:-1])


async def main():
    req = APIAsyncRequests()
    data = await req.get_users_info_by_vk_ids(user_ids=_user_ids, fields=items)
    print(data)
    data1 = await req.get_subscriptions_of_user_by_vk_id(226245594)
    print(data1)

if __name__ == '__main__':
    asyncio.run(main())


