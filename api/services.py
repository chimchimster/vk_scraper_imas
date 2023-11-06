from vk_scraper_imas.api.utils import do_post_request_to_vk_api


class APIAsyncRequests:

    API_LINK = 'https://api.vk.com/method/'

    @do_post_request_to_vk_api
    async def get_users_info_by_vk_ids(self, user_ids: list, **kwargs) -> str:
        """ Возвращает все возможные поля пользователя VK. """

        fields = kwargs.pop('fields')
        token = kwargs.pop('token')

        return await self.form_request_string(
            'users.get',
            user_ids=','.join(map(str, user_ids)),
            fields=','.join(fields),
            access_token=token,
            v=5.131,
        )

    @do_post_request_to_vk_api
    async def get_subscriptions_of_user_by_vk_id(self, user_id: list, **kwargs) -> str:
        """ Возвращает информацию о всех подписках пользователя. """

        fields = kwargs.pop('fields')
        token = kwargs.pop('token')
        offset = kwargs.pop('offset')

        return await self.form_request_string(
            'users.getSubscriptions',
            user_id=''.join(map(str, user_id)),
            fields=','.join(fields),
            extended=1,
            count=200,
            offset=offset,
            access_token=token,
            v=5.131,
        )

    @do_post_request_to_vk_api
    async def get_posts_by_vk_id(self, user_id: int, **kwargs) -> str:
        """ Возвращает информацию о всех постах на стене пользователя и/или группы. """

        token = kwargs.pop('token')

        return await self.form_request_string(
            'wall.get',
            owner_id=user_id,
            count=100,
            access_token=token,
            v=5.154,
        )

    async def form_request_string(self, method: str, **kwargs) -> str:

        kwargs = [f'{key}={val}&' for key, val in kwargs.items()]

        return self.API_LINK + """{}?{}""".format(method, ''.join(kwargs)[:-1])


