# 遞迴關係式精確解與 Big O 分析報告

本篇文件針對四個經典遞迴關係式進行逐步推導，求出精確解（閉合形式，Closed-form Solution）與 Big $O$ 漸近複雜度。

---

## 快速摘要表

| 編號 | 遞迴關係式 | 初始條件 | 精確解 $T(n)$ | Big $O$ |
| :---: | :--- | :---: | :--- | :---: |
| **1** | $T(n) = T(n-1) + 8$ | $T(1) = 1$ | $8n - 7$ | $O(n)$ |
| **2** | $T(n) = 2T(n-1) + 9$ | $T(1) = 1$ | $5 \cdot 2^n - 9$ (即 $10 \cdot 2^{n-1} - 9$) | $O(2^n)$ |
| **3** | $T(n) = 2T(n/2) + 1$ | $T(1) = 1$ | $2n - 1$ | $O(n)$ |
| **4** | $T(n) = T(n/2) + 1$ | $T(1) = 1$ | $\log_2 n + 1$ | $O(\log n)$ |

---

## 詳細推導過程

### 題目 1：$T(n) = T(n-1) + 8, \quad T(1) = 1$

#### 1. 展開法推導 (Iteration / Expansion Method)
$$
\begin{aligned}
T(n) &= T(n-1) + 8 \\
&= [T(n-2) + 8] + 8 = T(n-2) + 2 \cdot 8 \\
&= [T(n-3) + 8] + 2 \cdot 8 = T(n-3) + 3 \cdot 8 \\
&\;\;\vdots \\
&= T(n-k) + k \cdot 8
\end{aligned}
$$

#### 2. 終止條件代入
令 $n - k = 1$，得 $k = n - 1$：
$$
\begin{aligned}
T(n) &= T(1) + (n-1) \cdot 8 \\
&= 1 + 8n - 8 \\
&= 8n - 7
\end{aligned}
$$

- **精確解**：$T(n) = 8n - 7$
- **Big O**：$O(n)$

---

### 題目 2：$T(n) = 2T(n-1) + 9, \quad T(1) = 1$

#### 1. 展開法推導
$$
\begin{aligned}
T(n) &= 2T(n-1) + 9 \\
&= 2[2T(n-2) + 9] + 9 = 2^2 T(n-2) + 9(2 + 1) \\
&= 2^2[2T(n-3) + 9] + 9(2 + 1) = 2^3 T(n-3) + 9(2^2 + 2 + 1) \\
&\;\;\vdots \\
&= 2^k T(n-k) + 9 \sum_{i=0}^{k-1} 2^i
\end{aligned}
$$

#### 2. 終止條件代入
令 $n - k = 1$，得 $k = n - 1$：
$$
T(n) = 2^{n-1} T(1) + 9 \sum_{i=0}^{n-2} 2^i
$$

利用等比級數求和公式 $\sum_{i=0}^{m} r^i = \frac{r^{m+1}-1}{r-1}$（此處 $r=2, m=n-2$）：
$$
\sum_{i=0}^{n-2} 2^i = \frac{2^{(n-2)+1} - 1}{2 - 1} = 2^{n-1} - 1
$$

帶回原式，並代入 $T(1) = 1$：
$$
\begin{aligned}
T(n) &= 2^{n-1} \cdot 1 + 9(2^{n-1} - 1) \\
&= 10 \cdot 2^{n-1} - 9 \\
&= 5 \cdot (2 \cdot 2^{n-1}) - 9 \\
&= 5 \cdot 2^n - 9
\end{aligned}
$$

- **精確解**：$T(n) = 5 \cdot 2^n - 9$ （或寫為 $10 \cdot 2^{n-1} - 9$）
- **Big O**：$O(2^n)$

---

### 題目 3：$T(n) = 2T(n/2) + 1, \quad T(1) = 1$

> **假設**：設 $n = 2^k$（即 $k = \log_2 n$）。

#### 1. 展開法推導
$$
\begin{aligned}
T(n) &= 2T(n/2) + 1 \\
&= 2[2T(n/4) + 1] + 1 = 2^2 T(n/2^2) + (2 + 1) \\
&= 2^2[2T(n/8) + 1] + (2 + 1) = 2^3 T(n/2^3) + (2^2 + 2 + 1) \\
&\;\;\vdots \\
&= 2^k T(n/2^k) + \sum_{i=0}^{k-1} 2^i
\end{aligned}
$$

#### 2. 終止條件代入
令 $\frac{n}{2^k} = 1 \implies 2^k = n$ 且 $k = \log_2 n$：
$$
\begin{aligned}
T(n) &= n \cdot T(1) + (2^k - 1) \\
&= n \cdot 1 + (n - 1) \\
&= 2n - 1
\end{aligned}
$$

#### 3. Master Theorem 檢驗
對應形式 $T(n) = aT(n/b) + f(n)$：
- $a = 2, b = 2, f(n) = 1$
- 臨界指數：$n^{\log_b a} = n^{\log_2 2} = n^1 = n$
- 因 $f(n) = 1 = O(n^{1 - \epsilon})$（其中 $\epsilon = 1 > 0$），符合 Master Theorem Case 1。
- 結論：$T(n) = \Theta(n)$。

- **精確解**：$T(n) = 2n - 1$
- **Big O**：$O(n)$

---

### 題目 4：$T(n) = T(n/2) + 1, \quad T(1) = 1$

> **假設**：設 $n = 2^k$（即 $k = \log_2 n$）。

#### 1. 展開法推導
$$
\begin{aligned}
T(n) &= T(n/2) + 1 \\
&= [T(n/4) + 1] + 1 = T(n/2^2) + 2 \\
&= [T(n/8) + 1] + 2 = T(n/2^3) + 3 \\
&\;\;\vdots \\
&= T(n/2^k) + k
\end{aligned}
$$

#### 2. 終止條件代入
令 $\frac{n}{2^k} = 1 \implies k = \log_2 n$，代入 $T(1) = 1$：
$$
\begin{aligned}
T(n) &= T(1) + \log_2 n \\
&= 1 + \log_2 n
\end{aligned}
$$

*(註：若 $n$ 不限定為 2 的次方整數，通用整數閉合形式為 $\lfloor\log_2 n\rfloor + 1$。)*

#### 3. Master Theorem 檢驗
對應形式 $T(n) = aT(n/b) + f(n)$：
- $a = 1, b = 2, f(n) = 1$
- 臨界指數：$n^{\log_b a} = n^{\log_2 1} = n^0 = 1$
- 因 $f(n) = 1 = \Theta(n^{\log_b a})$，符合 Master Theorem Case 2。
- 結論：$T(n) = \Theta(n^0 \log n) = \Theta(\log n)$。

- **精確解**：$T(n) = \log_2 n + 1$
- **Big O**：$O(\log n)$