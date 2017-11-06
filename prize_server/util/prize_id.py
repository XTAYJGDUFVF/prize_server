import random
import bisect
from tornado.gen import coroutine

class WeightRandom:

    def __init__(self, items):
        weights = [w for _, w in items]
        self.id = [x for x, _ in items]
        self.total = sum(weights)
        self.acc = list(self.accumulate(weights))

    def accumulate(self, weights):  # 累和.如accumulate([10,40,50])->[10,50,100]
        cur = 0
        for w in weights:
            cur = cur + w
            yield cur

    def __call__(self):
        return self.id[bisect.bisect_right(self.acc, random.uniform(0, self.total))]


class Prize_Id:

    def __init__(self, prize_need_list):
        self.prize_need_list = prize_need_list
        weight_list = []
        for per in prize_need_list:
            for key, val in per.items():
                weight_list.append([key, val['probability']])
        self.weight_list = weight_list

    @coroutine
    def get_id(self):
        get_id_obj = WeightRandom(self.weight_list)
        return get_id_obj()
