# coding=utf-8

from motor.motor_tornado import MotorClient

from config import Config
from .util import Singleton, Utils


class MongoClientDelegateABC(Utils):

    def __init__(self, host):

        self._client = MotorClient(host)

    def get_client(self):

        return self._client


##########################################
# CLIENT USAGE

# 获取db
# db = client[r'db_name']

# 获取collection
# collection = client[r'db_name'][r'collection_name']

# 插入数据
# yield collection.insert_one(json_document)

# 查找一条数据
# yield collection.find_one({'key': {'$lt': 1}})

# 查找数据
# yield collection.find({'i': {'$lt': 5}}).sort('i').to_list()
# // .fetch_next()

# 查找文档条目
# yield collection.find(xxx).count()

# 替换文档
# yield collection.replace_one({'_id': _id}, {'key': 'value'})

# 更新文档
# yield collection.update_one({'i': 51}, {'$set': {'key': 'value'}})

# 批量更新文档
# yield collection.update_many({'i': {'$gt': 100}}, {'$set': {'key': 'value'}})

# 删除文档
# yield collection.delete_many({'i': {'$gte': 1000}})

# 其他命令
# yield db.command(SON([("count", "test_collection")]))
