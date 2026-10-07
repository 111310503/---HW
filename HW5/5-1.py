#方法一：遞迴解法
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

#方法二：非遞迴解法
def hanoi_iterative(n, source="A", target="C", auxiliary="B"):
    # 建立三根柱子的盤子堆疊
    pegs = {source: list(range(n, 0, -1)), auxiliary: [], target: []}

    total_moves = (1 << n) - 1

    # 根據 n 的奇偶性決定盤子 1 的循環順序
    if n % 2 == 1:
        cycle = [source, target, auxiliary]
    else:
        cycle = [source, auxiliary, target]

    pos1 = 0  # 盤子 1 目前所在柱子在 cycle 中的索引

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