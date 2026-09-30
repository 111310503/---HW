# 數值計算與機器學習迭代演算法技術文件

---

## 一、問題求解：利用數值方法求 $\sqrt{5}$ 的近似值

求解非線性方程式：
$$f(x) = x^2 - 5 = 0 \quad (x > 0)$$

求解此問題最常見且收斂快速的數值迭代法為**牛頓-拉弗森法（Newton-Raphson Method）**，應用於開平方根時又稱**巴比倫演算法（Babylonian Method）**。

---

### 1. 迭代公式推導

牛頓法的通用迭代公式為：
$$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}$$

已知：
* $f(x) = x^2 - 5$
* 一階導數 $f'(x) = 2x$

代入公式：
$$x_{k+1} = x_k - \frac{x_k^2 - 5}{2x_k} = \frac{2x_k^2 - (x_k^2 - 5)}{2x_k} = \frac{x_k^2 + 5}{2x_k}$$

化簡得開平方根專屬迭代公式：
$$x_{k+1} = \frac{1}{2} \left( x_k + \frac{5}{x_k} \right)$$

---

### 2. 手動計算過程

取初始猜測值 $x_0 = 2$（因 $2^2 = 4$ 最接近 $5$），計算至小數點後 6 位：

* **第 1 次迭代 ($k = 0$)：**
  $$x_1 = \frac{1}{2} \left( 2 + \frac{5}{2} \right) = \frac{1}{2} (2 + 2.5) = 2.25$$

* **第 2 次迭代 ($k = 1$)：**
  $$x_2 = \frac{1}{2} \left( 2.25 + \frac{5}{2.25} \right) \approx \frac{1}{2} (2.25 + 2.222222) = 2.236111$$

* **第 3 次迭代 ($k = 2$)：**
  $$x_3 = \frac{1}{2} \left( 2.236111 + \frac{5}{2.236111} \right) \approx \frac{1}{2} (2.236111 + 2.236068) = 2.236068$$

* **第 4 次迭代 ($k = 3$)：**
  $$x_4 = \frac{1}{2} \left( 2.236068 + \frac{5}{2.236068} \right) \approx 2.236068$$

> **收斂判定**：
> 當步進誤差滿足 $|x_4 - x_3| < 10^{-6}$，數值已完全收斂，得近似解：
> $$\sqrt{5} \approx 2.236068$$

---

## 二、經典數值與機器學習迭代演算法：統一抽象框架技術文件

### 1. 概述 (Overview)

本專案旨在展示**高階函數式抽象（Functional Abstraction）**在數值計算與機器學習演算法中的應用。

所有離散迭代演算法本質上均可視為一個**離散動力系統（Discrete Dynamical System）**：
$$S_{k+1} = \mathcal{T}(S_k)$$

* $S_k$：第 $k$ 步的系統狀態（State）
* $\mathcal{T}$：狀態推進算子（Transition Operator）

本專案將**控制流程**（迴圈控制、次數保護、收斂判定）與**數學邏輯**（狀態轉移算子）徹底解耦，透過單一核心引擎 `generic_iterator` 驅動 9 種橫跨數值分析、線性代數、微積分與統計機器學習的經典演算法。

---

### 2. 核心架構：通用迭代框架 (Core Framework)

#### 函式簽名
```python
generic_iterator(
    transition_func: Callable[[State], State],
    is_converged: Callable[[State, State, int], bool],
    initial_state: Any,
    max_iter: int = 1000
) -> Tuple[State, int]
```

核心函式採用**策略模式（Strategy Pattern）**的函數式實作：

| 參數名 | 類型 | 說明 |
| :--- | :--- | :--- |
| `transition_func` | `Callable[[State], State]` | 狀態轉移函數 $\mathcal{T}(S)$，接收前一步狀態並回傳下一步狀態 |
| `is_converged` | `Callable[[State, State, int], bool]` | 收斂檢查器，接收 `(old_state, new_state, iteration)` 並回傳布林值 |
| `initial_state` | `Any` | 系統初始狀態 $S_0$（支援純量、NumPy 陣列或 Tuple） |
| `max_iter` | `int` | 最大安全迭代步數，防止震盪或發散時陷入無窮迴圈（預設 `1000`） |

* **回傳值**：`(final_state, total_iterations)`

---

### 3. 範例演算法詳細說明 (Concrete Demonstrations)

#### 領域一：非線性方程式求根與最佳化

##### 1. 二維不動點迭代法 (`demo_fixed_point`)
* **數學原理**：求解多變數線性/非線性方程組的固定點 $X = G(X)$。依據巴拿赫不動點定理（Banach Fixed-Point Theorem），當轉移矩陣的譜半徑 $\rho(G) < 1$ 時，序列保證線性收斂。
* **狀態物件**：2 維 NumPy 向量 $\mathbf{x} = [x_1, x_2]^T$。
* **收斂依據**：相鄰兩步的 Euclidean 範數 $\|X_{k+1} - X_k\|_2 < 10^{-6}$。

##### 2. 牛頓-拉弗森法 (`demo_newton`)
* **數學原理**：求解方程式 $f(x) = x^2 - 4 = 0$ 的根。利用一階泰勒展開進行線性近似切線推進：
  $$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}$$
* **特性**：在單根鄰近區域具備二階收斂性（Quadratic Convergence）。
* **狀態物件**：浮點數純量 $x$。

---

#### 領域二：數值線性代數 (Numerical Linear Algebra)

##### 3. 高斯-賽得爾法 (`demo_gauss_seidel`)
* **數學原理**：求解大型稀疏線性方程組 $Ax = b$。核心技巧在於即時更新（Successive Displacement），計算第 $i$ 個分量時，立即套用當前輪次已更新的分量：
  $$x_i^{(k+1)} = \frac{1}{a_{ii}} \left( b_i - \sum_{j < i} a_{ij} x_j^{(k+1)} - \sum_{j > i} a_{ij} x_j^{(k)} \right)$$
* **收斂條件**：矩陣 $A$ 為嚴格對角佔優（Strictly Diagonally Dominant）或對稱正定（SPD）。
* **收斂依據**：無窮範數 $\|x^{(k+1)} - x^{(k)}\|_\infty < 10^{-6}$。

##### 4. 冪次迭代法 (`demo_power_iteration`)
* **數學原理**：提取矩陣 $A$ 絕對值最大的主特徵值與對應主特徵向量：
  $$v_{k+1} = \frac{Av_k}{\|Av_k\|}$$
  特徵值最後透過瑞利商（Rayleigh Quotient）計算：$\lambda \approx v^T A v$。
* **狀態物件**：單位化長度的特徵向量 $v$。

##### 5. QR 演算法 (`demo_qr_algorithm`)
* **數學原理**：計算矩陣全部特徵值的標準數值方法。將當前矩陣進行 QR 分解後顛倒順序相乘：
  $$A_k = Q_k R_k \implies A_{k+1} = R_k Q_k = Q_k^T A_k Q_k$$
  此為正交相似變換，逐步將 $A$ 驅動至舒爾形式（Schur Form，對稱矩陣則收斂為對角矩陣），對角線即為特徵值。
* **收斂依據**：非對角線元素的絕對值總和趨近於零。

---

#### 領域三：微分方程數值解 (ODEs)

##### 6. 四階龍格-庫塔法 (`demo_rk4`)
* **數學原理**：求解常微分方程初值問題 $\frac{dy}{dt} = f(t, y)$。利用區間內 4 個點的斜率加權平均推進狀態，單步局部截斷誤差為 $\mathcal{O}(h^5)$，整體全域誤差為 $\mathcal{O}(h^4)$。
* **狀態物件**：Tuple 結構 `(t, y)`。
* **收斂判斷**：將收斂條件設定為時間積分到達目標端點（$t \ge t_{end}$）。

---

#### 領域四：網路分析與機器學習 (Graph & Machine Learning)

##### 7. PageRank 隨機衝浪者模型 (`demo_pagerank`)
* **數學原理**：利用馬可夫鏈（Markov Chain）的平穩分佈評估網頁重要度。引入阻尼係數 $d = 0.85$ 解決 Spider Trap 與 Dead End 問題，構造 Google 轉移矩陣 $G$：
  $$G = d \cdot M + \frac{1 - d}{n} \mathbf{E}$$
  透過狀態轉移 $r_{k+1} = G r_k$ 迭代求解穩態分佈（Perron-Frobenius 定理）。

##### 8. K-Means 聚類演算法 (`demo_kmeans`)
* **數學原理**：無監督分群演算法，為 EM 演算法（硬分群 Hard-EM）的特例：
  * **E-step**：依據最小歐式距離分配各樣本至最近的群心。
  * **M-step**：將各群心更新為其所屬樣本點的幾何中心（均值）。
* **狀態物件**：群心矩陣 $\mathbf{C} \in \mathbb{R}^{K \times D}$。

##### 9. 期望最大化演算法 (`demo_em_two_coin`)
* **數學原理**：處理含潛在隱變數（Latent Variables）之統計模型的參數估計（以「雙硬幣投擲實驗」為例）：
  * **E-step**：在當前參數 $\theta = (\theta_A, \theta_B)$ 下，計算各實驗來自硬幣 A 或硬幣 B 的後驗期望機率。
  * **M-step**：透過加權後的正/反面總次數，最大化對數似然函數，更新下一輪硬幣正面的機率。
* **狀態物件**：機率二元組 `(theta_A, theta_B)`。

---

### 4. 模組比較總表

| 演算法 | 狀態類型 (State Type) | 終止 / 收斂條件型態 | 時間複雜度 / 每步 |
| :--- | :--- | :--- | :--- |
| **Fixed-Point** | 1D NumPy Array | 狀態差值的 $L_2$ 範數 | $\mathcal{O}(d)$ |
| **Newton's** | Float 純量 | 純量差值絕對值 | $\mathcal{O}(1)$ |
| **Gauss-Seidel** | 1D NumPy Array | 狀態差值的 $L_\infty$ 範數 | $\mathcal{O}(n^2)$ |
| **Power Iter.** | 1D NumPy Array | 向量方向穩定性 (`allclose`) | $\mathcal{O}(n^2)$ |
| **QR Algorithm**| 2D NumPy Array | 非對角線元素和接近 0 | $\mathcal{O}(n^3)$ |
| **RK4 ODE** | Tuple `(t, y)` | 時間軸抵達邊界 $t \ge t_{end}$ | $\mathcal{O}(1)$ |
| **PageRank** | 1D NumPy Array | 權重向量差值的 $L_2$ 範數 | $\mathcal{O}(n^2)$ |
| **K-Means** | 2D NumPy Array | 所有群心最大座標位移量 | $\mathcal{O}(N \cdot K \cdot D)$ |
| **EM (Two-Coin)**| Tuple `(float, float)` | 參數絕對變化值 | $\mathcal{O}(\text{trials})$ |

---

### 5. 執行環境與指令

```bash
# 建立並啟用虛擬環境 (可選)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝必要依賴套件
pip install numpy matplotlib

# 執行主程式
python main.py
```