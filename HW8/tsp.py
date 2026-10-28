import math
import random
import numpy as np


class TSPSolver:
    def __init__(self, cities: np.ndarray, seed: int = 42):
        """
        :param cities: (N, 2) 城市座標陣列
        :param seed: 亂數種子以保證可重現性
        """
        np.random.seed(seed)
        random.seed(seed)
        self.cities = cities
        self.num_cities = len(cities)
        self.dist_matrix = self._compute_dist_matrix()

    def _compute_dist_matrix(self) -> np.ndarray:
        diff = self.cities[:, np.newaxis, :] - self.cities[np.newaxis, :, :]
        return np.sqrt(np.sum(diff**2, axis=-1))

    def tour_length(self, tour: list) -> float:
        """計算給定迴圈路徑的總歐式距離"""
        dist = 0.0
        for i in range(len(tour)):
            dist += self.dist_matrix[tour[i], tour[(i + 1) % len(tour)]]
        return dist

    # -------------------------------------------------------------
    # 1. 改良法 (2-Opt Improvement)
    # -------------------------------------------------------------
    def solve_2opt(self, initial_tour: list = None) -> tuple:
        """
        透過不斷翻轉子區間以消除交叉邊的路徑改良法。
        """
        if initial_tour is None:
            tour = list(range(self.num_cities))
            random.shuffle(tour)
        else:
            tour = list(initial_tour)

        improved = True
        n = len(tour)

        while improved:
            improved = False
            best_gain = 0.0
            best_i, best_k = None, None

            for i in range(n - 1):
                for k in range(i + 2, n if i > 0 else n - 1):
                    a, b = tour[i], tour[i + 1]
                    c, d = tour[k], tour[(k + 1) % n]

                    current_dist = self.dist_matrix[a, b] + self.dist_matrix[c, d]
                    new_dist = self.dist_matrix[a, c] + self.dist_matrix[b, d]
                    gain = current_dist - new_dist

                    if gain > 1e-6 and gain > best_gain:
                        best_gain = gain
                        best_i, best_k = i, k

            if best_gain > 0.0:
                # 反轉 i+1 到 k 之間的城市順序
                tour[best_i + 1 : best_k + 1] = reversed(
                    tour[best_i + 1 : best_k + 1]
                )
                improved = True

        return tour, self.tour_length(tour)

    # -------------------------------------------------------------
    # 2. 爬山演算法 (Hill Climbing)
    # -------------------------------------------------------------
    def solve_hill_climbing(self, max_iter: int = 15000) -> tuple:
        """
        局部搜尋：每次在鄰域中隨機採樣交換/反轉，若更好則移動。
        """
        current_tour = list(range(self.num_cities))
        random.shuffle(current_tour)
        current_cost = self.tour_length(current_tour)

        for _ in range(max_iter):
            # 隨機產生 2-opt 翻轉鄰居
            i, k = sorted(random.sample(range(self.num_cities), 2))
            if k - i <= 1 or (i == 0 and k == self.num_cities - 1):
                continue

            neighbor = list(current_tour)
            neighbor[i:k] = reversed(neighbor[i:k])
            neighbor_cost = self.tour_length(neighbor)

            if neighbor_cost < current_cost:
                current_tour = neighbor
                current_cost = neighbor_cost

        return current_tour, current_cost

    # -------------------------------------------------------------
    # 3. 模擬退火法 (Simulated Annealing)
    # -------------------------------------------------------------
    def solve_simulated_annealing(
        self,
        t_init: float = 100.0,
        t_min: float = 1e-4,
        alpha: float = 0.995,
        steps_per_temp: int = 100,
    ) -> tuple:
        """
        透過 Metropolis 準則，以可控機率接受較差解跳脫局部最優。
        """
        current_tour = list(range(self.num_cities))
        random.shuffle(current_tour)
        current_cost = self.tour_length(current_tour)

        best_tour = list(current_tour)
        best_cost = current_cost
        t = t_init

        while t > t_min:
            for _ in range(steps_per_temp):
                i, k = sorted(random.sample(range(self.num_cities), 2))
                if k - i <= 1:
                    continue

                candidate = list(current_tour)
                candidate[i:k] = reversed(candidate[i:k])
                candidate_cost = self.tour_length(candidate)

                delta = candidate_cost - current_cost
                if delta < 0 or math.exp(-delta / t) > random.random():
                    current_tour = candidate
                    current_cost = candidate_cost

                    if current_cost < best_cost:
                        best_tour = list(current_tour)
                        best_cost = current_cost

            t *= alpha

        return best_tour, best_cost

    # -------------------------------------------------------------
    # 4. 梯度下降法 (Continuous Relaxation + Adam Optimizer)
    # -------------------------------------------------------------
    def solve_gradient_descent(
        self, steps: int = 1200, lr: float = 0.05
    ) -> tuple:
        """
        將離散排列鬆弛為雙隨機 Softmax 矩陣，透過可微分期望長度梯度下降求解。
        最後貪婪解碼為合法排列。
        """
        n = self.num_cities
        # W: (N, N) 代表步驟 t 拜訪城市 i 的未正規化權重
        W = np.random.randn(n, n) * 0.1
        m = np.zeros_like(W)
        v = np.zeros_like(W)
        beta1, beta2, eps = 0.9, 0.999, 1e-8

        for step in range(1, steps + 1):
            # Softmax 沿城市維度 (每個時間步僅選一個城市)
            exp_w = np.exp(W - np.max(W, axis=1, keepdims=True))
            P = exp_w / (np.sum(exp_w, axis=1, keepdims=True) + 1e-12)

            # 計算連續期望距離 Loss = Tr(P_t * D * P_{t+1}^T)
            # P_next 為下一個時間步的機率分布 (循環)
            P_next = np.roll(P, -1, axis=0)
            P_prev = np.roll(P, 1, axis=0)

            # 計算梯度 dLoss/dP
            grad_P = P_next @ self.dist_matrix.T + P_prev @ self.dist_matrix

            # Softmax 反向傳播鏈鎖法則
            p_dot_grad = np.sum(P * grad_P, axis=1, keepdims=True)
            grad_W = P * (grad_P - p_dot_grad)

            # 加入行正則化（防止不同時間步選同一個城市）
            col_penalty = np.sum(P, axis=0, keepdims=True) - 1.0
            grad_W += 0.05 * (P * (col_penalty - np.sum(P * col_penalty, axis=1, keepdims=True)))

            # Adam 更新權重
            m = beta1 * m + (1 - beta1) * grad_W
            v = beta2 * v + (1 - beta2) * (grad_W**2)
            m_hat = m / (1 - beta1**step)
            v_hat = v / (1 - beta2**step)
            W -= lr * m_hat / (np.sqrt(v_hat) + eps)

        # 解碼：貪婪分配離散路徑
        final_P = np.exp(W - np.max(W, axis=1, keepdims=True))
        final_P = final_P / np.sum(final_P, axis=1, keepdims=True)

        visited = set()
        tour = []
        for t in range(n):
            ranking = np.argsort(-final_P[t])
            for city in ranking:
                if city not in visited:
                    visited.add(city)
                    tour.append(int(city))
                    break

        # 填補未造訪城市（防呆保護）
        for c in range(n):
            if c not in visited:
                tour.append(c)

        return tour, self.tour_length(tour)

    # -------------------------------------------------------------
    # 5. 貪婪演算法 (Nearest Neighbor)
    # -------------------------------------------------------------
    def solve_greedy_nearest_neighbor(self, start_city: int = 0) -> tuple:
        """
        每一步皆選擇尚未造訪且距離當前最近的城市。
        """
        unvisited = set(range(self.num_cities))
        tour = [start_city]
        unvisited.remove(start_city)

        current = start_city
        while unvisited:
            next_city = min(unvisited, key=lambda c: self.dist_matrix[current, c])
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city

        return tour, self.tour_length(tour)


# =================================================================
# 執行範例與成果比較
# =================================================================
if __name__ == "__main__":
    NUM_CITIES = 20
    np.random.seed(101)
    test_cities = np.random.rand(NUM_CITIES, 2) * 100

    solver = TSPSolver(test_cities, seed=42)

    print(f"=== 旅行推銷員問題 (TSP) 求解比較 (城市數量: {NUM_CITIES}) ===")

    # 1. 貪婪演算法
    tour_greedy, cost_greedy = solver.solve_greedy_nearest_neighbor()
    print(f"5. 貪婪演算法 (Nearest Neighbor) : 總距離 = {cost_greedy:.3f}")

    # 2. 改良法 (以貪婪解為初始路線)
    tour_2opt, cost_2opt = solver.solve_2opt(initial_tour=tour_greedy)
    print(f"1. 改良法 (2-Opt on Greedy)     : 總距離 = {cost_2opt:.3f}")

    # 3. 爬山演算法
    tour_hc, cost_hc = solver.solve_hill_climbing()
    print(f"2. 爬山演算法 (Hill Climbing)     : 總距離 = {cost_hc:.3f}")

    # 4. 模擬退火法
    tour_sa, cost_sa = solver.solve_simulated_annealing()
    print(f"3. 模擬退火法 (Simulated Annealing): 總距離 = {cost_sa:.3f}")

    # 5. 梯度下降法 (連續鬆弛)
    tour_gd, cost_gd = solver.solve_gradient_descent()
    print(f"4. 梯度下降法 (Continuous Relax)  : 總距離 = {cost_gd:.3f}")