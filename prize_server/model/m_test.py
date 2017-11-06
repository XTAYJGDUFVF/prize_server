from .base import BaseModel
from tornado.gen import coroutine
from controller.base import RequestBaseHandler
from util.decorator import catch_error

class Tests(BaseModel):

    @coroutine
    def test(self):
        with catch_error():
            db_client = self.get_db_transaction()
            print(db_client)
            db_client = self.get_db_client()
            print(db_client)
            res = yield db_client.insert('game_score_info', user_id=127, insure_score=19)
            # print(res)
            # res = yield db_client.select('game_score_info', what='user_id')
            # print(res)
            # res = yield db_client.update('game_score_info', where={'user_id': 126}, insure_score=111)
            # print(res)
            # res = yield db_client.increase_update('game_score_info', where={'user_id': 128}, fields1={'insure_score': 5})
            # print(res)
