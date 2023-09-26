from .utils import do_post_request_to_vk_api


class APIAsyncRequests:

    API_LINK = 'https://api.vk.com/method/'

    @do_post_request_to_vk_api
    async def get_users_info_by_vk_ids(self, user_ids: list, **kwargs) -> str:
        """ Возвращает все возможные поля пользователя VK. """

        fields = kwargs.pop('fields')
        token = kwargs.pop('token')

        return await self.form_request_string(
            'users.get',
            user_ids=','.join(user_ids),
            fields=','.join(fields),
            access_token=token,
            v=5.131,
        )

    @do_post_request_to_vk_api
    async def get_subscriptions_of_user_by_vk_id(self, user_id: int, **kwargs) -> str:
        """ Возвращает информацию о всех подписках пользователя. """

        fields = kwargs.pop('fields')
        token = kwargs.pop('token')

        return await self.form_request_string(
            'users.getSubscriptions',
            user_id=user_id,
            fields=','.join(fields),
            extended=1,
            access_token=token,
            v=5.131,
        )

    async def form_request_string(self, method: str, **kwargs) -> str:

        kwargs = [f'{key}={val}&' for key, val in kwargs.items()]

        return self.API_LINK + """{}?{}""".format(method, ''.join(kwargs)[:-1])


# async def main():
#     req = APIAsyncRequests()
#
#     path_to_users_JSON = pathlib.Path('./schemas/user_fields.JSON')
#     path_to_groups_JSON = pathlib.Path('./schemas/group_fields.JSON')
#
#     user_fields = await read_schema(path_to_users_JSON)
#     user_fields = user_fields.get('user_fields')
#     group_fields = await read_schema(path_to_groups_JSON)
#     group_fields = group_fields.get('group_fields')
#
#     data = await req.get_users_info_by_vk_ids(user_ids=_user_ids, fields=user_fields)
#     data1 = await req.get_subscriptions_of_user_by_vk_id(226245594, fields=user_fields+group_fields)
#
#     lst = []
#     for usr in data1.get('response').get('items'):
#         print(usr)
#         try:
#             obj = VKUser.model_validate(usr)
#             lst.append(obj)
#         except ValidationError:
#             obj = SubscribedToGroup.model_validate(usr)
#             lst.append(obj)
#
#     print(lst)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


