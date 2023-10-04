from typing import Final
from .db_handler import APIStateDB

SUBSCRIBED_TO_GROUP_RATE_LIMIT: Final[int] = 3


class APIRateLimitsValidator:

    def __init__(self, obj_name: str, token: str):
        self._obj_name = obj_name
        self._token = token

    @property
    def obj_name(self) -> str:
        return self._obj_name

    @property
    def token(self) -> str:
        return self._token

    async def validate_state_before_request(self):
        """ Валидация состояния связи токен-объект запроса
            (создание состояния, в случае если такого состояния нет). """

        validator = APIStateDB()

        await validator.insert_token(self.token)
        await validator.insert_vk_object(self.obj_name)
        await validator.create_state(self.obj_name, self.token)

    async def validate_state_after_request(self, signal: bool = False) -> bool:

        validator = APIStateDB()

        await validator.update_state(self.obj_name, self.token, expired=signal)

        return validator.validation_instance



# 1. Добавить токен в базу, если в базе его еще нет
# 2. Добавить имя объекта запроса в базу, если в базе его еще нет
# 3. Создать состояние для пары токен-объект запроса, если в базе его еще нет
# 4. Если состояние уже есть:
# 4.1. В случае, если поле expired принимает значение false и
# 4.1. сработал сигнал о нарушении рейт лимита: изменить поле expired с False на True, обновить время expired_at
# 4.1. Валидация не проходит, токен и объект возвращаются в очередь задач
# 4.2. В случае, если поле expired принимает значение True: сравнить разницу между текущим временем и last_use
# 4.3. Если разница между текущим временем и last use > 24ч, изменить поле expired на False
# 4.4. В случае, если разница меньше 24ч, валидация не проходит, токен и объект возвращаются в очередь задач
# 4.5. В случае, если сигнала о нарушении рейт лимита не поступало, увеличить счетчик поля requests на 1, обновить время last_use

