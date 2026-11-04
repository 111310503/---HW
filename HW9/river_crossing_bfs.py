"""
問題 2: 狼羊甘藍菜過河問題 (BFS - 廣度優先搜尋)
說明:
- 狀態表示: (farmer, wolf, sheep, cabbage)，0 代表左岸，1 代表右岸。
- 目標是尋找步數最短（最少擺渡次數）的合法安全過河解。
"""

from collections import deque

def is_valid_state(state):
    f, w, s, c = state
    # 農夫不在時，狼與羊不能同側
    if w == s and f != w:
        return False
    # 農夫不在時，羊與甘藍菜不能同側
    if s == c and f != s:
        return False
    return True

def get_next_states(state):
    f, w, s, c = state
    next_f = 1 - f
    candidates = []

    # 1. 農夫自己單獨過河
    candidates.append(((next_f, w, s, c), "農夫獨自過河"))

    # 2. 農夫帶狼
    if f == w:
        candidates.append(((next_f, next_f, s, c), "農夫帶【狼】過河"))
    # 3. 農夫帶羊
    if f == s:
        candidates.append(((next_f, w, next_f, c), "農夫帶【羊】過河"))
    # 4. 農夫帶甘藍菜
    if f == c:
        candidates.append(((next_f, w, s, next_f), "農夫帶【甘藍菜】過河"))

    # 過濾不合法狀態
    return [(st, act) for st, act in candidates if is_valid_state(st)]

def solve_river_crossing_bfs():
    initial_state = (0, 0, 0, 0)
    goal_state = (1, 1, 1, 1)

    # 佇列記錄: (當前狀態, 歷史操作與狀態路徑)
    queue = deque([(initial_state, [])])
    visited = {initial_state}

    while queue:
        current, history = queue.popleft()

        if current == goal_state:
            return history

        for next_st, action in get_next_states(current):
            if next_st not in visited:
                visited.add(next_st)
                queue.append((next_st, history + [(action, next_st)]))

    return None

if __name__ == "__main__":
    solution = solve_river_crossing_bfs()
    print("="*20 + " 狼羊甘藍菜過河最少步數解 (BFS) " + "="*20)
    if solution:
        print(f"初始狀態: 全部在左岸 (0, 0, 0, 0)\n")
        for step, (act, st) in enumerate(solution, 1):
            side = ["左岸", "右岸"]
            state_desc = f"農夫:{side[st[0]]}, 狼:{side[st[1]]}, 羊:{side[st[2]]}, 菜:{side[st[3]]}"
            print(f"步驟 {step}: {act:<14} -> [{state_desc}]")
        print(f"\n總共花費步數: {len(solution)} 步")
    else:
        print("無解。")