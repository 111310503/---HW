"""
問題 5: IC 設計中的電路繞線 (Lee's Maze Router - 李氏迷宮繞線法)
說明:
- 基於 BFS 波前擴展 (Wavefront Expansion)，保證找到最短連線路徑。
- 支援多條連線 (Nets) 依序繞線，已繞完的線路自動標記為後續 net 的障礙物。
"""

from collections import deque

class GridRouter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 0: 空白, -1: 障礙物/已佔用繞線
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def add_obstacle(self, x, y):
        self.grid[y][x] = -1

    def route_net(self, pin_source, pin_target):
        sx, sy = pin_source
        tx, ty = pin_target

        if self.grid[sy][sx] == -1 or self.grid[ty][tx] == -1:
            return None

        # 1. 波前擴展 (Expansion)
        wave_grid = [row[:] for row in self.grid]
        queue = deque([(sx, sy)])
        wave_grid[sy][sx] = 1  # 初始波標記

        found = False
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == (tx, ty):
                found = True
                break

            curr_dist = wave_grid[cy][cx]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if wave_grid[ny][nx] == 0:  # 未走過且非障礙
                        wave_grid[ny][nx] = curr_dist + 1
                        queue.append((nx, ny))

        if not found:
            return None

        # 2. 回溯尋路 (Retrace / Backtrace)
        path = [(tx, ty)]
        curr = (tx, ty)

        while curr != (sx, sy):
            cx, cy = curr
            curr_val = wave_grid[cy][cx]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if wave_grid[ny][nx] == curr_val - 1:
                        path.append((nx, ny))
                        curr = (nx, ny)
                        break

        path.reverse()

        # 3. 清理並鎖定資源 (標記為已佔用障礙物)
        for px, py in path:
            self.grid[py][px] = -1

        return path

    def display(self):
        for row in self.grid:
            print(" ".join(["X" if cell == -1 else "." for cell in row]))
        print()

if __name__ == "__main__":
    router = GridRouter(width=10, height=8)

    # 設置晶片佈局障礙物
    for y in range(2, 6):
        router.add_obstacle(4, y)

    nets = [
        ("NetA", (1, 3), (7, 3)),
        ("NetB", (2, 1), (2, 6))
    ]

    for net_name, src, dst in nets:
        path = router.route_net(src, dst)
        if path:
            print(f"[{net_name}] 繞線成功 (長度: {len(path)}): {path}")
        else:
            print(f"[{net_name}] 繞線失敗 (無可用路徑)")

    print("\n繞線後的晶片網格佔用情況 (X: 障礙物或金屬線, .: 空白):")
    router.display()