def sym_diff(expr, var='x'):
    """
    對符號表達式 expr 針對變數 var 做遞迴微分
    回傳微分後的符號樹結構
    """
    # 1. 基底條件：常數與變數
    if isinstance(expr, (int, float)):
        return 0
    
    if isinstance(expr, str):
        return 1 if expr == var else 0

    # 2. 遞迴條件：根據運算子應用微積分法則
    op = expr[0]

    # 一元運算（函式）
    if op == 'sin':
        # d/dx sin(u) = cos(u) * u'
        u = expr[1]
        return simplify(('*', ('cos', u), sym_diff(u, var)))

    elif op == 'cos':
        # d/dx cos(u) = -sin(u) * u'
        u = expr[1]
        return simplify(('*', ('-', 0, ('sin', u)), sym_diff(u, var)))

    elif op == 'ln':
        # d/dx ln(u) = (1/u) * u'
        u = expr[1]
        return simplify(('*', ('/', 1, u), sym_diff(u, var)))

    # 二元運算
    u, v = expr[1], expr[2]
    du = sym_diff(u, var)
    dv = sym_diff(v, var)

    if op == '+':
        # 加法法則：(u + v)' = u' + v'
        return simplify(('+', du, dv))

    elif op == '-':
        # 減法法則：(u - v)' = u' - v'
        return simplify(('-', du, dv))

    elif op == '*':
        # 乘法法則（Product Rule）：(u * v)' = u' * v + u * v'
        term1 = ('*', du, v)
        term2 = ('*', u, dv)
        return simplify(('+', term1, term2))

    elif op == '/':
        # 除法法則（Quotient Rule）：(u / v)' = (u' * v - u * v') / (v^2)
        numerator = ('-', ('*', du, v), ('*', u, dv))
        denominator = ('^', v, 2)
        return simplify(('/', numerator, denominator))

    elif op == '^':
        # 次方法則（Power Rule，假設指數為常數 n）：(u^n)' = n * u^(n-1) * u'
        if isinstance(v, (int, float)):
            power_term = ('^', u, v - 1) if v - 1 != 1 else u
            return simplify(('*', ('*', v, power_term), du))
        else:
            # 一般化指數式 u^v：d/dx e^(v * ln(u))
            # (u^v)' = u^v * (v' * ln(u) + v * u' / u)
            return simplify(('*', expr, sym_diff(('*', v, ('ln', u)), var)))

    raise ValueError(f"不支援的運算子: {op}")


def simplify(expr):
    """
    遞迴簡化代數表達式（移除 0、1 等多餘運算）
    """
    if isinstance(expr, (int, float, str)):
        return expr

    op = expr[0]

    # 一元節點
    if len(expr) == 2:
        arg = simplify(expr[1])
        return (op, arg)

    # 二元節點
    left = simplify(expr[1])
    right = simplify(expr[2])

    # 兩側皆為常數直接折疊（Constant Folding）
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/' and right != 0: return left / right
        if op == '^': return left ** right

    # 恆等與零元簡化
    if op == '+':
        if left == 0: return right
        if right == 0: return left

    elif op == '-':
        if right == 0: return left
        if left == right: return 0

    elif op == '*':
        if left == 0 or right == 0: return 0
        if left == 1: return right
        if right == 1: return left

    elif op == '/':
        if left == 0: return 0
        if right == 1: return left

    elif op == '^':
        if right == 0: return 1
        if right == 1: return left
        if left == 0: return 0

    return (op, left, right)


def to_str(expr):
    """將表達式樹轉為可讀字串"""
    if isinstance(expr, (int, float, str)):
        return str(expr)
    if len(expr) == 2:
        return f"{expr[0]}({to_str(expr[1])})"
    op, left, right = expr
    return f"({to_str(left)} {op} {to_str(right)})"