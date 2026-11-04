"""
問題 1: 老鼠走迷宮問題 (DFS - 深度優先搜尋)
說明:
- 0 代表通道，1 代表牆壁。
- 使用遞迴與回溯法 (Backtracking) 尋找從起點到終點的一條可行路徑。
"""

def solve_maze_dfs(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    visited = set()
    path = []

    def dfs(r, c):
        # 邊界與障礙物檢查
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if maze[r][c] == 1 or (r, c) in visited:
            return False

        # 標記訪問並加入當前路徑
        visited.add((r, c))
        path.append((r, c))

        # 到達目標
        if (r, c) == goal:
            return True

        # 四個移動方向：上、下、左、右
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            if dfs(r + dr, c + dc):
                return True

        # 回溯 (Backtrack)
        path.pop()
        return False

    if dfs(start[0], start[1]):
        return path
    return None

def print_maze_solution(maze, path):
    grid = [["#" if cell == 1 else " " for cell in row] for row in maze]
    if path:
        for r, c in path:
            grid[r][c] = "."
        start, goal = path[0], path[-1]
        grid[start[0]][start[1]] = "S"
        grid[goal[0]][goal[1]] = "G"

    print("\n" + "="*25 + " 迷宮路徑 " + "="*25)
    for row in grid:
        print(" ".join(row))
    print("="*60)

if __name__ == "__main__":
    maze_map = [
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0]
    ]
    start_pos = (0, 0)
    goal_pos = (4, 5)

    result_path = solve_maze_dfs(maze_map, start_pos, goal_pos)
    if result_path:
        print(f"找到路徑 (步數: {len(result_path)}): {result_path}")
        print_maze_solution(maze_map, result_path)
    else:
        print("無路可達目標。")