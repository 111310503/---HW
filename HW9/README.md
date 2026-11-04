# 經典搜尋演算法與工程應用解析專案

本專案實作並解析了電腦科學五大經典搜尋問題，涵蓋**無資訊搜尋 (Uninformed Search)**、**約束滿足回溯 (CSP / Backtracking)**、**啟發式搜尋 (Heuristic Search)** 以及在 **電子設計自動化 (EDA / VLSI Design)** 中廣泛應用的佈線搜尋方法。

---

## 檔案架構

```text
├── maze_dfs.py              # 1. 老鼠走迷宮問題 (DFS)
├── river_crossing_bfs.py    # 2. 狼羊甘藍菜過河問題 (BFS)
├── eight_queens_dfs.py      # 3. 八皇后問題 (DFS / Backtracking)
├── npc_pathfinding_astar.py # 4. NPC 尋路玩家問題 (A*)
├── ic_routing_lee.py        # 5. IC 設計電路繞線問題 (Lee's Maze Router)
└── README.md                # 演算法原理與工程理論詳細說明文件
```

---

## 1. 老鼠走迷宮問題 (DFS)

### 1.1 原理與機制
* **演算法**：深度優先搜尋（Depth-First Search, DFS）。
* **策略**：沿著單一路徑向下探索到底，遭遇死胡同或障礙時，透過堆疊（Call Stack）回溯至上一個分歧點，並轉向另一分支探索。
* **狀態標記**：透過 `visited` 集合記錄已走訪坐標，防止陷入無限迴圈。

### 1.2 複雜度分析
* **時間複雜度**：$O(V + E)$，其中 $V = R \times C$（網格總數），$E \le 4V$。最差情況需遍歷所有可通行的格子。
* **空間複雜度**：$O(V)$，用於維持系統遞迴呼叫堆疊與走訪標記。
* **特點**：不保證能求出步數最短的路徑，但能以極低記憶體開銷迅速找到一條可行通解。

---

## 2. 狼羊甘藍菜過河問題 (BFS)

### 2.1 原理與狀態空間建構
* **演算法**：廣度優先搜尋（Breadth-First Search, BFS）。
* **狀態編碼**：以四元組表示狀態：
  $$
  \text{State} = (F, W, G, C)
  $$
  其中數值 $0$ 代表在左岸，$1$ 代表在右岸。
* **合法性約束（Constraints）**：
  * 當農夫不在時，狼與羊不能獨處：若 $F \neq G \land W = G$，狀態非法。
  * 當農夫不在時，羊與甘藍菜不能獨處：若 $F \neq G \land G = C$，狀態非法。
* **狀態轉移**：農夫必須在船上，每次可選擇「單獨過河」或「攜帶同岸的一件物品過河」。

### 2.2 最優性保證
在每一步過河操作權重均為 $1$ 的情況下，BFS 具備**按層擴展（Level-order traversal）**的特性，保證首次到達目標狀態 $(1, 1, 1, 1)$ 時，該路徑即為步驟最少的最優解。

---

## 3. 八皇后問題 (DFS / Backtracking)

### 3.1 原理與約束滿足問題 (CSP)
在 $8 \times 8$ 的西洋棋盤上放置 8 個皇后，使其互不威脅。
* 傳統枚舉需要檢驗 $\binom{64}{8} \approx 4.4 \times 10^9$ 種可能。
* 採用 DFS 回溯法將問題轉化為**逐行配置**：第 $r$ 行必定只能放一個皇后。

### 3.2 剪枝條件 (Pruning)
利用三個雜湊集合即時檢驗約束，時間複雜度為 $O(1)$：
1. **直列衝突**：列編號 $c$ 是否已被佔用。
2. **主對角線衝突**：對於正斜率對角線，其值滿足 $r - c = \text{常數}$。
3. **副對角線衝突**：對於負斜率對角線，其值滿足 $r + c = \text{常數}$。

若某一位置發生衝突則立即剪枝回溯，大幅縮減搜尋樹的分支數。8 皇后總共有 92 組解。

---

## 4. NPC 搜尋玩家問題 (A*)

### 4.1 原理與啟發評估函數
* **演算法**：A\* 啟發式搜尋演算法（A\* Search Algorithm）。
* **評估函數**：
  $$
  f(n) = g(n) + h(n)
  $$
  * $g(n)$：從 NPC 起點移動到當前節點 $n$ 的實際成本。
  * $h(n)$：從節點 $n$ 到玩家位置的預估成本（Heuristic）。

### 4.2 啟發函數的可接受性 (Admissibility)
在四向移動的網格中，選用**曼哈頓距離（Manhattan Distance）**：
$$
h(n) = \vert{}x_n - x_{\text{target}}\vert{} + \vert{}y_n - y_{\text{target}}\vert{}
$$
由於曼哈頓距離永不高估實際剩餘代價（$h(n) \le h^*(n)$），A\* 保證能找到追蹤玩家的最短路徑，且優先展開朝向玩家方向的節點，探索效率遠勝 Dijkstra 與 BFS。

---

## 5. IC 設計中的電路繞線問題 (VLSI Routing)

在晶片實體設計（Physical Design）中，繞線階段需要將各邏輯單元的接腳（Pins）利用多層金屬線相互連接，且必須遵守嚴格的幾何設計規則（DRC）。

### 5.1 經典搜尋繞線演算法

1. **李氏迷宮繞線演算法 (Lee's Maze Router)**
   * **原理**：二維/三維網格上的 BFS 波前擴展（Wavefront Expansion）。
   * **流程**：從起點 Pin 開始依步數逐層擴展標記網格，抵達終點後再由終點沿著數值遞減方向回溯（Backtrace）生成走線。
   * **優缺點**：保證能找到最短繞線，但空間與時間複雜度均達 $O(M \times N)$。

2. **霍頓繞線演算法 (Hadlock's Detour Router)**
   * **原理**：引入 A\* 啟發式思想的網格繞線法。
   * **機制**：計算走線偏離目標的「繞道數（Detour Number）」。優先擴展繞道數最小的走線波前，搜尋區域從李氏演算法的圓形波前收縮為橢圓形，大幅減少運算節點。

3. **蘇謝演算法 (Soukup's Router)**
   * **原理**：結合 DFS 與 BFS 的混合策略。
   * **機制**：沿著目標方向以 DFS 高速前進，遭遇障礙物時再切換為 BFS 繞行障礙，繞過後立即恢復 DFS，大幅提升大晶片佈線速度。

### 5.2 現代兩階段繞線架構 (Modern Two-Stage Routing)
面對現代晶片數十億連線（Nets），無法直接進行全圖詳細繞線，業界普遍採用兩階段繞線：

* **全域繞線 (Global Routing)**：
  * 將晶片劃分為粗粒度的 G-Cells（Global Cells）。
  * 採用**斯坦納最小樹（Steiner Minimal Tree, 如 FLUTE 演算法）**計算拓撲，並利用協商擁擠繞線演算法（如 **PathFinder**）平衡各通道的金屬線密度。
* **詳細繞線 (Detailed Routing)**：
  * 在各 G-Cell 細部網格中，利用改良版 A\* 與迷宮繞線演算法指定金屬層與實體軌道，嚴格符合線距、線寬與通孔（Via）等 DRC 規範。

---

## 6. 演算法特性與綜合比較

| 問題 | 核心演算法 | 搜尋類別 | 時間複雜度 | 空間複雜度 | 最優性保證 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **老鼠走迷宮** | DFS | 盲目搜尋 | $O(V + E)$ | $O(V)$ | 否 |
| **狼羊過河** | BFS | 盲目搜尋 | $O(b^d)$ | $O(b^d)$ | 是（最少步數） |
| **八皇后問題** | DFS / 回溯 | 約束滿足 / 剪枝 | $O(N!)$ | $O(N)$ | 是（窮舉全解） |
| **NPC 尋路** | A\* Search | 啟發式搜尋 | $O(E \log V)$ | $O(V)$ | 是（$h$ 符合 Admissible） |
| **IC 電路繞線** | Lee / Hadlock / A\* | 網格波前 / Detour | $O(W \cdot H)$ | $O(W \cdot H)$ | 是（單條 Net 最短） |

---

## 執行方式

每個 Python 檔案均內建測試案例，可直接於終端機執行：

```bash
python maze_dfs.py
python river_crossing_bfs.py
python eight_queens_dfs.py
python npc_pathfinding_astar.py
python ic_routing_lee.py
```