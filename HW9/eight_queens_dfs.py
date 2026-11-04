"""
問題 3: 八皇后問題 (DFS - 深度優先搜尋 + 回溯剪枝)
說明:
- 在 8x8 棋盤上擺放 8 個皇后，使其互不攻擊（同行、同列、同對角線）。
- queens[row] = col 表示第 row 列的皇后放在第 col 行。
"""

def solve_n_queens_dfs(n=8):
    solutions = []
    board = [-1] * n

    # 集合加速剪枝檢查: O(1) 判定衝突
    cols = set()
    diag1 = set()  # 主對角線: r - c
    diag2 = set()  # 副對角線: r + c

    def backtrack(row):
        if row == n:
            solutions.append(list(board))
            return

        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue

            # 放置皇后並更新狀態
            board[row] = col
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)

            backtrack(row + 1)

            # 回溯還原
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)
            board[row] = -1

    backtrack(0)
    return solutions

def print_board(solution):
    n = len(solution)
    for r in range(n):
        line = ["Q" if solution[r] == c else "." for c in range(n)]
        print(" ".join(line))
    print()

if __name__ == "__main__":
    n = 8
    all_solutions = solve_n_queens_dfs(n)
    print(f"=== {n} 皇后問題解法總數: {len(all_solutions)} 組 ===")
    print("展示第 1 組解的棋盤佈局:\n")
    print_board(all_solutions[0])