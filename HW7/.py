import time
from typing import List, Union

Sequence = Union[str, List[str]]


def diff_dp(A: Sequence, B: Sequence) -> str:
    """
    方法一：使用標準動態規劃 (Longest Common Subsequence, LCS) 實作 diff
    時間複雜度: O(M * N)
    空間複雜度: O(M * N)
    """
    M, N = len(A), len(B)
    # 建立 (M+1) x (N+1) 的 DP 表格
    dp = [[0] * (N + 1) for _ in range(M + 1)]

    # 填表：計算 LCS 長度
    for i in range(1, M + 1):
        for j in range(1, N + 1):
            if A[i - 1] == B[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 回溯：從右下角往左上角找出差異步驟
    i, j = M, N
    diff_result = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and A[i - 1] == B[j - 1]:
            diff_result.append(f"  {A[i - 1]}")
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
            diff_result.append(f"+ {B[j - 1]}")
            j -= 1
        else:
            diff_result.append(f"- {A[i - 1]}")
            i -= 1

    return "\n".join(reversed(diff_result))


def diff_myers(A: Sequence, B: Sequence) -> str:
    """
    方法二：使用 Myers 差分演算法 (圖論 BFS + 對角線貪婪滑行) 實作 diff
    時間複雜度: O((M + N) * D)，其中 D 為最小編輯距離
    空間複雜度: O(D^2) 用於儲存回溯軌跡
    """
    M, N = len(A), len(B)
    max_d = M + N
    # V[k] 記錄在斜線 k = x - y 上能到達的最大 x 座標
    V = {1: 0}
    trace = []

    # 1. 前向貪婪搜尋：依編輯距離 D 逐步擴展
    for d in range(max_d + 1):
        trace.append(V.copy())
        for k in range(-d, d + 1, 2):
            # 決定是從 k-1 往右走(刪除)，還是從 k+1 往下走(新增)
            # 貪婪策略：選擇能讓起始 x 座標更大的那條路
            if k == -d or (k != d and V.get(k - 1, -1) < V.get(k + 1, -1)):
                x = V.get(k + 1, 0)      # 從上方 (k+1) 往下走，x 不變
            else:
                x = V.get(k - 1, 0) + 1  # 從左方 (k-1) 往右走，x + 1

            y = x - k

            # 對角線免費滑行 (Snake)：遇到相同元素直接推進
            while x < M and y < N and A[x] == B[y]:
                x += 1
                y += 1

            V[k] = x

            # 抵達終點 (M, N)，立即結束搜尋並開始回溯
            if x >= M and y >= N:
                return _backtrack_myers(A, B, trace, d)

    return ""


def _backtrack_myers(A: Sequence, B: Sequence, trace: list, d: int) -> str:
    """Myers 演算法的反向路徑回溯輔助函式"""
    x, y = len(A), len(B)
    diff_result = []

    # 2. 反向回溯路徑 (從 D 退回 1)
    for step_d in range(d, 0, -1):
        V = trace[step_d]
        k = x - y

        if k == -step_d or (k != step_d and V.get(k - 1, -1) < V.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1

        prev_x = V[prev_k]
        prev_y = prev_x - prev_k

        # 先回溯對角線滑行的部分 (相同元素)
        while x > prev_x and y > prev_y:
            diff_result.append(f"  {A[x - 1]}")
            x -= 1
            y -= 1

        # 再記錄當步的新增或刪除
        if x == prev_x:
            diff_result.append(f"+ {B[prev_y]}")
        else:
            diff_result.append(f"- {A[prev_x]}")

        x, y = prev_x, prev_y

    # 處理 D=0 時開頭完全相同的對角線部分
    while x > 0 and y > 0:
        diff_result.append(f"  {A[x - 1]}")
        x -= 1
        y -= 1

    return "\n".join(reversed(diff_result))


if __name__ == "__main__":
    # 範例 1：經典字串比對
    str_A = "ABCABBA"
    str_B = "CBABAC"

    print("=" * 40)
    print(f"測試字串 A: {str_A}")
    print(f"測試字串 B: {str_B}")
    print("=" * 40)

    print("\n【1. 動態規劃 (LCS) 輸出結果】:")
    print(diff_dp(str_A, str_B))

    print("\n【2. Myers 演算法 輸出結果】:")
    print(diff_myers(str_A, str_B))

    # 範例 2：大型且高相似度序列的效能對比 (模擬大型程式碼微幅修改)
    print("\n" + "=" * 40)
    print("效能測試：長度 1500 的序列，僅修改其中 2 處 (D 極小)")
    print("=" * 40)

    large_A = [f"line_{i}" for i in range(1500)]
    large_B = large_A.copy()
    large_B[500] = "modified_line_500"
    large_B.pop(1000)

    start_dp = time.perf_counter()
    diff_dp(large_A, large_B)
    time_dp = (time.perf_counter() - start_dp) * 1000

    start_myers = time.perf_counter()
    diff_myers(large_A, large_B)
    time_myers = (time.perf_counter() - start_myers) * 1000

    print(f"動態規劃 (LCS) 耗時: {time_dp:.2f} ms")
    print(f"Myers 演算法   耗時: {time_myers:.2f} ms")
    if time_myers > 0:
        print(f"👉 Myers 演算法在此高相似度場景快了約 {time_dp / time_myers:.1f} 倍！")