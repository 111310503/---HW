# $2^n$ 演算法效能與複雜度評測報告

本專案實作並評測了四種在 Python 中計算 $2^n$ 的演算法，針對 $n = 100$ 的場景進行時間複雜度、空間複雜度以及執行可行性之詳細分析。

---

## 1. 實作程式碼 (`power2n.py`)

```python
import sys
import time

# 方法 1：內建次方運算子
def power2n_1(n):
    return 2 ** n

# 方法 2a：雙遞迴加法（無快取）
def power2n_2a(n):
    if n == 0:
        return 1
    return power2n_2a(n - 1) + power2n_2a(n - 1)

# 方法 2b：單遞迴乘法（線性遞迴）
def power2n_2b(n):
    if n == 0:
        return 1
    return 2 * power2n_2b(n - 1)

# 方法 3：遞迴 + 查表（記憶化 Memoization）
def power2n_3(n, memo=None):
    if memo is None:
        memo = {}
    if n == 0:
        return 1
    if n in memo:
        return memo[n]
    memo[n] = power2n_3(n - 1, memo) + power2n_3(n - 1, memo)
    return memo[n]

def benchmark(func, n, name, skip_heavy=False):
    print(f"--- 測試 {name} (n={n}) ---")
    if skip_heavy:
        print("狀態: [已略過] 計算複雜度達 O(2^n)，無法在有限時間內產出結果。\n")
        return

    try:
        start_time = time.perf_counter()
        result = func(n)
        elapsed = time.perf_counter() - start_time
        
        str_res = str(result)
        display_res = (
            str_res if len(str_res) <= 20 
            else f"{str_res[:6]}...{str_res[-6:]} (共 {len(str_res)} 位數)"
        )
        print(f"結果: {display_res}")
        print(f"耗時: {elapsed:.8f} 秒\n")
    except RecursionError:
        print("狀態: [遞迴崩潰] 超過 Python 預設遞迴上限 (RecursionError)。\n")
    except Exception as e:
        print(f"狀態: [錯誤] {e}\n")

if __name__ == "__main__":
    print(f"目前 Python 遞迴深度限制: {sys.getrecursionlimit()}\n")
    test_n = 100

    # 1. 內建運算子
    benchmark(power2n_1, test_n, "方法 1: 內建運算子 (2**n)")

    # 2a. 雙遞迴加法 (n=100 會卡死，設為 skip_heavy 以免程式當機)
    benchmark(power2n_2a, test_n, "方法 2a: 雙遞迴加法", skip_heavy=True)

    # 2b. 單遞迴乘法
    benchmark(power2n_2b, test_n, "方法 2b: 單遞迴乘法")

    # 3. 遞迴 + 查表
    benchmark(power2n_3, test_n, "方法 3: 遞迴+查表 (Memoization)")

    # 補充：方法 2a 在較小測資 (n=25) 下的實際執行
    small_n = 25
    print(f"=== 補充測試：方法 2a 在小測資 (n={small_n}) 下的耗時 ===")
    benchmark(power2n_2a, small_n, f"方法 2a (n={small_n})")
```

---

## 2. 演算法複雜度與可行性比較

針對 $n = 100$：

| 方法 | 核心運算 | 時間複雜度 | 空間複雜度 | $n=100$ 是否能產出 | 預估耗時 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **方法 1** | `2 ** n` | $O(\log n)$ | $O(1)$ | **能** | $< 0.000002$ 秒 |
| **方法 2a** | `f(n-1) + f(n-1)` | $O(2^n)$ | $O(n)$ | **出不來 (卡死)** | 約 $8 \times 10^{13}$ 年 |
| **方法 2b** | `2 * f(n-1)` | $O(n)$ | $O(n)$ | **能** | $\approx 0.000015$ 秒 |
| **方法 3** | `f(n-1) + f(n-1)` + `memo` | $O(n)$ | $O(n)$ | **能** | $\approx 0.000030$ 秒 |

---

## 3. 測試問題解答

### Q1：哪個快？哪個慢？
1. **最快：方法 1 (`2 ** n`)**
   - 採用 Python/C 階層實作的快速冪演算法，直接在二進位底層做位移與乘法，耗時僅在微秒級以下。
2. **第二快：方法 2b (`2 * f(n-1)`)**
   - 僅呼叫 $100$ 次遞迴堆疊，為單純的線性乘法，比查表省略了雜湊表（`dict`）的查詢與插入開銷。
3. **第三快：方法 3 (遞迴 + 查表)**
   - 雖然呼叫結構為二元樹，但查表保證每個子狀態只計算一次，時間被剪枝壓縮為 $O(n)$，效能依舊非常快。
4. **最慢（且出不來）：方法 2a (`f(n-1) + f(n-1)`)**

### Q2：哪個出不來？為什麼？
- **方法 2a 完全出不來**。
- **原因分析**：
  - 此方法會展開成一個深度為 100 的完全二元樹。
  - 總遞迴呼叫次數為：
    $$2^{101} - 1 \approx 2.53 \times 10^{30} \text{ 次}$$
  - 即使使用現代超級電腦每秒執行 $10^9$ 次遞迴呼叫，所需時間仍高達：
    $$\frac{2.53 \times 10^{30}}{10^9 \times 3600 \times 24 \times 365} \approx 8.04 \times 10^{13} \text{ 年}$$
  - 因此在一般電腦上執行此演算法時，程式會呈現永久無回應（卡死）狀態。

---

## 4. 延伸討論：遞迴深度限制 (Recursion Limit)

當測試測資提高至 $n > 1000$（如 $n = 1500$）時：
- **方法 1** 仍可正常計算（Python 的大整數無位元上限限制）。
- **方法 2b** 與 **方法 3** 會拋出 `RecursionError: maximum recursion depth exceeded`。
- 若需遞迴處理超大測資，可透過 `sys.setrecursionlimit(...)` 調整上限，或改用迭代迴圈（`for` 迴圈）實作以避免堆疊溢位。