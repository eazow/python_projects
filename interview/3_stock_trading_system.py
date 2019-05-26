# -*- coding: utf-8 -*-
#
# 时间复杂度O(n), 因为只用了一次循环
# 空间复杂度O(1)


import sys


def get_max_profit(prices):
    """
    获取最大利润
    :return:
    """

    first_buy_min_cost = sys.maxint
    second_buy_min_cost = sys.maxint

    first_sell_max_profit = - sys.maxint
    second_sell_max_profit = - sys.maxint

    for price in prices:
        # 第一次买的最小成本
        first_buy_min_cost = min(first_buy_min_cost, price)
        # 第一次卖的最大收益
        first_sell_max_profit = max(first_sell_max_profit, price-first_buy_min_cost)
        # 第二次买的最小成本
        second_buy_min_cost = min(second_buy_min_cost, price - first_sell_max_profit)
        # 第二次卖的最大收益
        second_sell_max_profit = max(second_sell_max_profit, price - second_buy_min_cost)

    return second_sell_max_profit


if __name__ == '__main__':
    assert get_max_profit([1, 2, 3, 4, 5, 6]) == 5
    assert get_max_profit([3, 3, 5, 0, 0, 3, 1, 4]) == 6
