"""
數值微積分與蒙地卡羅積分實作 (Numerical Calculus & Monte Carlo Integration)
"""

import math
import random
import itertools
import time


# ==========================================
# 1. 單變數數值微分與積分
# ==========================================
def diff_1d(f, x, h=1e-5):
    """使用中央差分法計算單變數函數在 x 點的數值微分"""
    return (f(x + h) - f(x - h)) / (2 * h)


def riemann_1d(f, low, high, n=10000):
    """使用中點黎曼和計算單變數定積分"""
    dx = (high - low) / n
    total = 0.0
    for i in range(n):
        mid = low + (i + 0.5) * dx
        total += f(mid)
    return total * dx


# ==========================================
# 2. 蒙地卡羅法單變數積分
# ==========================================
def mc_integral_1d(f, low, high, samples=100000):
    """使用蒙地卡羅法計算單變數定積分"""
    total = 0.0
    for _ in range(samples):
        x = random.uniform(low, high)
        total += f(x)
    return (high - low) * (total / samples)


# ==========================================
# 3. n 變數數值微分（梯度）
# ==========================================
def gradient(f, x, h=1e-5):
    """計算 n 變數函數在點 x (list) 的梯度向量"""
    grad = []
    for i in range(len(x)):
        x_plus = list(x)
        x_minus = list(x)
        x_plus[i] += h
        x_minus[i] -= h
        df_dxi = (f(x_plus) - f(x_minus)) / (2 * h)
        grad.append(df_dxi)
    return grad


# ==========================================
# 3 & 5. 黎曼積分法做 n 變數積分（超體積）
# ==========================================
def integral(f, low, high, steps=10, max_points=1_000_000):
    """
    使用中點黎曼和計算 n 變數定積分（超體積）
    :param f: 接受長度為 n 的 list/tuple 的函數
    :param low: 各維度下界陣列
    :param high: 各維度上界陣列
    :param steps: 每個維度的切割數
    :param max_points: 防止維度災難導致當機的最大網格點數上限
    """
    n = len(low)
    total_points = steps ** n

    if total_points > max_points:
        raise OverflowError(
            f"維度災難警告：{n} 維空間每維切 {steps} 份需要計算 {steps}^{n} "
            f"(約 {total_points:.2e}) 個點，超過上限 {max_points:,}，無法於合理時間內完成。"
        )

    dx = [(high[i] - low[i]) / steps for i in range(n)]
    cell_volume = math.prod(dx)

    # 產生每個維度的中點座標
    axes = [
        [low[i] + (k + 0.5) * dx[i] for k in range(steps)]
        for i in range(n)
    ]

    total = 0.0
    for point in itertools.product(*axes):
        total += f(point)

    return total * cell_volume


# ==========================================
# 4 & 6. 蒙地卡羅法做 n 變數積分（超體積）
# ==========================================
def mc_integral(f, low, high, samples=100000):
    """
    使用蒙地卡羅法計算 n 變數定積分（超體積）
    :param f: 接受長度為 n 的 list 的函數
    :param low: 各維度下界陣列
    :param high: 各維度上界陣列
    :param samples: 隨機取樣次數
    """
    n = len(low)
    volume = math.prod(high[i] - low[i] for i in range(n))

    total = 0.0
    for _ in range(samples):
        point = [random.uniform(low[i], high[i]) for i in range(n)]
        total += f(point)

    return volume * (total / samples)


# ==========================================
# 測試範例
# ==========================================
def run_tests():
    random.seed(42)  # 固定隨機種子以利重現結果

    print("=== 1. 單變數數值微分與積分 ===")
    # 範例：f(x) = x^2，在 x=3 處微分為 6，在 [0, 1] 積分值為 1/3 ≈ 0.333333
    f1 = lambda x: x ** 2
    print(f"f(x) = x^2 在 x=3 的微分: {diff_1d(f1, 3):.6f} (理論值: 6.000000)")
    print(f"f(x) = x^2 在 [0, 1] 的黎曼積分: {riemann_1d(f1, 0, 1):.6f} (理論值: {1/3:.6f})\n")

    print("=== 2. 蒙地卡羅法單變數積分 ===")
    print(f"f(x) = x^2 在 [0, 1] 的蒙地卡羅積分: {mc_integral_1d(f1, 0, 1):.6f} (理論值: {1/3:.6f})\n")

    print("=== 3. n 變數數值微分（梯度） ===")
    # 範例：f(x, y, z) = x^2 + 2y^2 + 3z^2，在 (1, 2, 3) 的梯度為 [2, 8, 18]
    f_multi = lambda p: p[0]**2 + 2*(p[1]**2) + 3*(p[2]**2)
    grad = gradient(f_multi, [1.0, 2.0, 3.0])
    print(f"f(x,y,z) = x^2 + 2y^2 + 3z^2 在 (1,2,3) 的梯度: {[round(g, 4) for g in grad]} (理論值: [2.0, 8.0, 18.0])\n")

    # 題目 5 & 6 共用測試函數：f(x) = x1^2 + x2^2 + ... + xn^2，範圍 [0, 1]^n
    # 理論解析解：∫(x1^2 + ... + xn^2) dx = n * (1/3) = n / 3
    sum_of_squares = lambda x: sum(xi ** 2 for xi in x)
    dimensions = [1, 2, 5, 100]

    print("=== 5. 黎曼積分法計算 n 變數積分 (f(x) = x1^2 + ... + xn^2, [0, 1]^n) ===")
    for n in dimensions:
        low = [0.0] * n
        high = [1.0] * n
        exact = n / 3.0
        # 依據維度調整每維切割數，避免低維太粗或中維太慢
        steps = 1000 if n == 1 else (100 if n == 2 else 10)
        start = time.time()
        try:
            res = integral(sum_of_squares, low, high, steps=steps)
            elapsed = time.time() - start
            print(f"{n:3d} 維 | 黎曼積分 = {res:9.6f} | 理論值 = {exact:9.6f} | 誤差 = {abs(res - exact):.6f} | 耗時: {elapsed:.4f}s (每維切 {steps} 份)")
        except OverflowError as e:
            print(f"{n:3d} 維 | 計算中止 -> {e}")

    print("\n=== 6. 蒙地卡羅法計算 n 變數積分 (f(x) = x1^2 + ... + xn^2, [0, 1]^n) ===")
    samples = 100_000
    for n in dimensions:
        low = [0.0] * n
        high = [1.0] * n
        exact = n / 3.0
        start = time.time()
        res = mc_integral(sum_of_squares, low, high, samples=samples)
        elapsed = time.time() - start
        print(f"{n:3d} 維 | 蒙地卡羅 = {res:9.6f} | 理論值 = {exact:9.6f} | 誤差 = {abs(res - exact):.6f} | 耗時: {elapsed:.4f}s (取樣 {samples:,} 次)")


if __name__ == "__main__":
    run_tests()