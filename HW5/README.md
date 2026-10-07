# 遞迴與函數式編程實戰筆記

本文件整理了三個經典進階演算法與概念的剖析與實作：
1. **河內塔問題（遞迴與非遞迴解法）**
2. **符號數學式微分（語法樹與遞迴展開）**
3. **自製高階函數與無迴圈泡沫排序**

---

## 5-1 河內塔問題（Tower of Hanoi）

### 1. 方法一：遞迴解法（Recursive）
核心邏輯是將問題拆解為三個子步驟：
1. 先將上方 $n-1$ 個盤子從 A 移到 B（以 C 為輔助）。
2. 將第 $n$ 個（最大的）盤子直接從 A 移到 C。
3. 再將剛才放在 B 的 $n-1$ 個盤子移到 C（以 A 為輔助）。

#### 實作程式碼
```python
def hanoi_recursive(n, source, target, auxiliary):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return

    # 1. 將 n-1 個盤子從 source 移到 auxiliary
    hanoi_recursive(n - 1, source, auxiliary, target)

    # 2. 將最大的盤子從 source 移到 target
    print(f"Move disk {n} from {source} to {target}")

    # 3. 將 n-1 個盤子從 auxiliary 移到 target
    hanoi_recursive(n - 1, auxiliary, target, source)


# 測試：移動 3 個盤子
hanoi_recursive(3, "A", "C", "B")
```

---

### 2. 方法二：非遞迴解法（Iterative）
移動 $n$ 個盤子的最小總步數為 $2^n - 1$。採用**二進位與輪轉規律**，每一步都有固定規則：

1. **奇數盤與偶數盤的循環方向不同**：
   - 若 $n$ 為奇數：盤子 1 每次依 `A -> C -> B -> A` 的方向前進。
   - 若 $n$ 為偶數：盤子 1 每次依 `A -> B -> C -> A` 的方向前進。
2. **走法交替**：
   - 奇數步（1, 3, 5...）：移動「盤子 1」（最小的盤子）。
   - 偶數步（2, 4, 6...）：在不包含盤子 1 的另外兩根柱子之間，做「唯一合法」的移動（將較小的盤子移到較大的盤子上）。

#### 實作程式碼
```python
def hanoi_iterative(n, source="A", target="C", auxiliary="B"):
    pegs = {source: list(range(n, 0, -1)), auxiliary: [], target: []}
    total_moves = (1 << n) - 1

    # 根據 n 的奇偶性決定盤子 1 的循環順序
    cycle = [source, target, auxiliary] if n % 2 == 1 else [source, auxiliary, target]
    pos1 = 0

    def make_legal_move(p1, p2):
        """在兩根柱子間執行唯一合法的移動"""
        if not pegs[p1]:
            disk = pegs[p2].pop()
            pegs[p1].append(disk)
            print(f"Move disk {disk} from {p2} to {p1}")
        elif not pegs[p2]:
            disk = pegs[p1].pop()
            pegs[p2].append(disk)
            print(f"Move disk {disk} from {p1} to {p2}")
        elif pegs[p1][-1] < pegs[p2][-1]:
            disk = pegs[p1].pop()
            pegs[p2].append(disk)
            print(f"Move disk {disk} from {p1} to {p2}")
        else:
            disk = pegs[p2].pop()
            pegs[p1].append(disk)
            print(f"Move disk {disk} from {p2} to {p1}")

    for step in range(1, total_moves + 1):
        if step % 2 == 1:
            # 奇數步：移動盤子 1
            curr_peg = cycle[pos1]
            pos1 = (pos1 + 1) % 3
            next_peg = cycle[pos1]
            disk = pegs[curr_peg].pop()
            pegs[next_peg].append(disk)
            print(f"Move disk 1 from {curr_peg} to {next_peg}")
        else:
            # 偶數步：移動另外兩根柱子中合法的盤子
            other_pegs = [p for p in [source, auxiliary, target] if p != cycle[pos1]]
            make_legal_move(other_pegs[0], other_pegs[1])


# 測試：移動 3 個盤子
hanoi_iterative(3, "A", "C", "B")
```

---

## 5-2 符號數學式微分（Symbolic Differentiation）

符號微分是遞迴結構的典型應用。數學表達式本質上是一棵**抽象語法樹（AST）**，只要針對基底條件（常數、變數）與運算子節點（加、減、乘、除、次方等微積分法則）定義遞迴展開式即可。

### 微積分轉換對應

| 節點類型 | 數學公式 | 遞迴轉換規則 |
|---|---|---|
| 常數 $c$ | $\frac{d}{dx} c = 0$ | 回傳 `0` |
| 變數 $x$ | $\frac{d}{dx} x = 1$ | 變數相符回傳 `1`，否則 `0` |
| 和差 $u \pm v$ | $(u \pm v)' = u' \pm v'$ | `('+', du, dv)` |
| 乘法 $u \cdot v$ | $(uv)' = u'v + uv'$ | `('+', ('*', du, v), ('*', u, dv))` |
| 除法 $\frac{u}{v}$ | $(\frac{u}{v})' = \frac{u'v - uv'}{v^2}$ | `('/', ('-', ('*', du, v), ('*', u, dv)), ('^', v, 2))` |

#### 實作程式碼
```python
def sym_diff(expr, var='x'):
    """對表達式樹 expr 針對變數 var 進行遞迴符號微分"""
    # 1. 基底條件
    if isinstance(expr, (int, float)):
        return 0
    if isinstance(expr, str):
        return 1 if expr == var else 0

    op = expr[0]

    # 一元函數
    if op == 'sin':
        u = expr[1]
        return simplify(('*', ('cos', u), sym_diff(u, var)))
    elif op == 'cos':
        u = expr[1]
        return simplify(('*', ('-', 0, ('sin', u)), sym_diff(u, var)))

    # 二元運算
    u, v = expr[1], expr[2]
    du = sym_diff(u, var)
    dv = sym_diff(v, var)

    if op == '+':
        return simplify(('+', du, dv))
    elif op == '-':
        return simplify(('-', du, dv))
    elif op == '*':
        return simplify(('+', ('*', du, v), ('*', u, dv)))
    elif op == '/':
        numerator = ('-', ('*', du, v), ('*', u, dv))
        denominator = ('^', v, 2)
        return simplify(('/', numerator, denominator))
    elif op == '^':
        if isinstance(v, (int, float)):
            power_term = ('^', u, v - 1) if v - 1 != 1 else u
            return simplify(('*', ('*', v, power_term), du))

    raise ValueError(f"不支援的運算子: {op}")


def simplify(expr):
    """簡化代數節點（移除加 0、乘 1 等）"""
    if isinstance(expr, (int, float, str)):
        return expr

    op = expr[0]
    if len(expr) == 2:
        return (op, simplify(expr[1]))

    left, right = simplify(expr[1]), simplify(expr[2])

    # 常數折疊
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right

    if op == '+':
        if left == 0: return right
        if right == 0: return left
    elif op == '-':
        if right == 0: return left
    elif op == '*':
        if left == 0 or right == 0: return 0
        if left == 1: return right
        if right == 1: return left

    return (op, left, right)
```

---

## 5-3 自製高階函數與無迴圈泡沫排序

### 1. 自製 `my_map`, `my_filter`, `my_reduce`
三個函數皆以「遞迴拆解串列（Head + Tail）」的方式實作，完全禁止使用迴圈：

```python
def my_map(func, lst):
    """自製 map"""
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])


def my_filter(predicate, lst):
    """自製 filter"""
    if not lst:
        return []
    head, tail = lst[0], my_filter(predicate, lst[1:])
    return [head] + tail if predicate(head) else tail


def my_reduce(func, lst, initial=None):
    """自製 reduce"""
    if not lst:
        if initial is None:
            raise TypeError("my_reduce() of empty sequence with no initial value")
        return initial

    if initial is None:
        return my_reduce(func, lst[1:], lst[0])

    return my_reduce(func, lst[1:], func(initial, lst[0]))
```

---

### 2. 無迴圈泡沫排序（Bubble Sort）

傳統泡沫排序由兩層迴圈構成：
- **內層掃描**：兩兩相鄰元素比較，將當前最大值「浮」至最右側。
- **外層輪次**：重複執行 $n-1$ 次內層掃描。

#### 透過 `my_reduce` 實現「單趟浮動（One Pass）」
在單趟掃描中，使用 `my_reduce` 來維護一個狀態 `(processed_list, current_max)`：
- 遍歷下一個元素 $x$ 時：
  - 若 $x \ge current\_max$，將舊的 $current\_max$ 放進已處理列表，更新最大值為 $x$。
  - 若 $x < current\_max$，將 $x$ 放進已處理列表，維持 $current\_max$。
- 遍歷結束後，將最後留下的 $current\_max$ 附加到末尾，即完成一次最大值後移。

#### 透過遞迴實現「多輪收斂」
每次外層遞迴將串列長度規模縮小 1，直到只剩 0 或 1 個元素。

#### 實作程式碼
```python
def bubble_pass(lst):
    """利用自製 my_reduce 執行單趟相鄰比較與冒泡"""
    if len(lst) <= 1:
        return lst

    def step(acc, item):
        elems, cur_max = acc
        if item < cur_max:
            # cur_max 較大，item 留在前面，cur_max 繼續向後浮
            return (elems + [item], cur_max)
        else:
            # item 較大，舊 cur_max 留下，item 變成新的最大值向後浮
            return (elems + [cur_max], item)

    processed, final_max = my_reduce(step, lst[1:], ([], lst[0]))
    return processed + [final_max]


def bubble_sort(lst):
    """外層遞迴：重複進行冒泡，直到整個串列有序"""
    if len(lst) <= 1:
        return lst

    # 1. 執行單趟冒泡，確保最後一個元素必定是整體最大值
    passed = bubble_pass(lst)

    # 2. 前 n-1 個元素遞迴排序，再拼回最大值
    return bubble_sort(passed[:-1]) + [passed[-1]]


# 測試驗證
data = [64, 34, 25, 12, 22, 11, 90, 5, 42]
print("排序結果:", bubble_sort(data))
# 輸出: [5, 11, 12, 22, 25, 34, 42, 64, 90]
```