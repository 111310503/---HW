"""
問題 4: NPC 搜尋玩家問題 (A* 啟發式搜尋)
說明:
- 評估函數 f(n) = g(n) + h(n)
- g(n): 起點到目前點的實際移動代價
- h(n): 曼哈頓距離 (Manhattan Distance)，作為啟發式函數估算
"""

import heapq

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_star_search(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    
    # 優先權佇列項目: (f_score, g_score, current_pos)
    open_heap = []
    heapq.heappush(open_heap, (manhattan_distance(start, goal), 0, start))
    
    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    while open_heap:
        _, current_g, current = heapq.heappop(open_heap)

        if current == goal:
            # 重建路徑
            path = []
            curr = goal
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            return path[::-1]

        if current in closed_set:
            continue
        closed_set.add(current)

        # 上、下、左、右移動
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dr, current[1] + dc)
            nr, nc = neighbor

            # 地圖邊界與障礙物判斷
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if grid[nr][nc] == 1:
                continue

            tentative_g = current_g + 1

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan_distance(neighbor, goal)
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

    return None

if __name__ == "__main__":
    # 0: 平地, 1: 障礙物/牆壁
    game_map = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 0, 0, 0]
    ]
    npc_pos = (0, 0)
    player_pos = (4, 4)

    path = a_star_search(game_map, npc_pos, player_pos)
    print(f"NPC 尋找玩家的最佳導航路徑 (長度 {len(path) - 1} 步):")
    print(path)