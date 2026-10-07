def my_map(func, lst):
    """自製 map：對串列中每個元素套用 func"""
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])


def my_filter(predicate, lst):
    """自製 filter：保留滿足 predicate(x) is True 的元素"""
    if not lst:
        return []
    head, tail = lst[0], my_filter(predicate, lst[1:])
    return [head] + tail if predicate(head) else tail


def my_reduce(func, lst, initial=None):
    """自製 reduce：以累積方式將雙變數函式折疊整個串列"""
    if not lst:
        if initial is None:
            raise TypeError("my_reduce() of empty sequence with no initial value")
        return initial

    if initial is None:
        # 沒有提供初始值時，取第一個元素為初始值
        return my_reduce(func, lst[1:], lst[0])

    return my_reduce(func, lst[1:], func(initial, lst[0]))