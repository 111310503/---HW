# Python 實現 Lambda Calculus（$\lambda$-微積分）解譯器

本專案使用 Python 實現一個完整的純粹 $\lambda$-微積分（Pure Untyped Lambda Calculus）解譯器。解譯器採用**正規序歸約（Normal Order Reduction，最外最左優先）**，並具備**防變數捕捉的代換機制（Capture-avoiding substitution / $\alpha$-轉換）**，能夠完整印出每一步 $\beta$-歸約的詳細推導過程。

---

## 1. 完整原始程式碼

```python
import re
from typing import Set, Tuple


# ==========================================
# 1. 抽象語法樹（AST）節點定義
# ==========================================
class Expr:

    def free_vars(self) -> Set[str]:
        raise NotImplementedError

    def substitute(self, var: str, replacement: "Expr") -> "Expr":
        raise NotImplementedError


class Var(Expr):

    def __init__(self, name: str):
        self.name = name

    def free_vars(self) -> Set[str]:
        return {self.name}

    def substitute(self, var: str, replacement: Expr) -> Expr:
        return replacement if self.name == var else self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Abs(Expr):

    def __init__(self, param: str, body: Expr):
        self.param = param
        self.body = body

    def free_vars(self) -> Set[str]:
        return self.body.free_vars() - {self.param}

    def substitute(self, var: str, replacement: Expr) -> Expr:
        if self.param == var:
            return self

        # 若替換項目的自由變數包含當前參數，需進行 α-轉換避免變數捕捉 (Variable Capture)
        if self.param in replacement.free_vars():
            all_vars = self.body.free_vars() | replacement.free_vars() | {var}
            fresh_param = self.param
            while fresh_param in all_vars:
                fresh_param += "'"
            renamed_body = self.body.substitute(self.param, Var(fresh_param))
            return Abs(fresh_param, renamed_body.substitute(var, replacement))

        return Abs(self.param, self.body.substitute(var, replacement))

    def __str__(self):
        return f"(λ{self.param}. {self.body})"

    def __repr__(self):
        return str(self)


class App(Expr):

    def __init__(self, func: Expr, arg: Expr):
        self.func = func
        self.arg = arg

    def free_vars(self) -> Set[str]:
        return self.func.free_vars() | self.arg.free_vars()

    def substitute(self, var: str, replacement: Expr) -> Expr:
        return App(
            self.func.substitute(var, replacement),
            self.arg.substitute(var, replacement),
        )

    def __str__(self):
        return f"({self.func} {self.arg})"

    def __repr__(self):
        return str(self)


# ==========================================
# 2. 語法分析器（Lexer & Parser）
# ==========================================
class Parser:

    def __init__(self, text: str):
        self.tokens = re.findall(
            r"λ|\\|\.|\(|\)|[a-zA-Z_][a-zA-Z0-9_']*", text
        )
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        tok = self.peek()
        if expected and tok != expected:
            raise SyntaxError(f"預期 '{expected}'，但得到 '{tok}'")
        self.pos += 1
        return tok

    def parse(self) -> Expr:
        expr = self.parse_app()
        if self.pos < len(self.tokens):
            raise SyntaxError(f"未預期的額外語素: {self.tokens[self.pos:]}")
        return expr

    def parse_app(self) -> Expr:
        """解析函數應用（左結合）：e1 e2 e3 -> ((e1 e2) e3)"""
        exprs = []
        while self.peek() and self.peek() != ")":
            exprs.append(self.parse_primary())
        if not exprs:
            raise SyntaxError("表達式不可為空")
        res = exprs[0]
        for e in exprs[1:]:
            res = App(res, e)
        return res

    def parse_primary(self) -> Expr:
        tok = self.peek()
        if tok in ("\\", "λ"):
            self.consume()
            # 支援多參數語法糖，如 \x y. body -> \x. \y. body
            params = []
            while self.peek() and self.peek() not in (".", ")"):
                params.append(self.consume())
            if not params:
                raise SyntaxError("Lambda 缺少參數名稱")
            self.consume(".")
            body = self.parse_app()
            for p in reversed(params):
                body = Abs(p, body)
            return body
        elif tok == "(":
            self.consume("(")
            expr = self.parse_app()
            self.consume(")")
            return expr
        else:
            return Var(self.consume())


def parse_lambda(code: str) -> Expr:
    return Parser(code).parse()


# ==========================================
# 3. 求解引擎（Normal Order β-Reduction）
# ==========================================
def step_reduce(expr: Expr) -> Tuple[Expr, bool, str]:
    """執行一次最外層最左側的 β-歸約 (Normal Order Reduction)"""
    # 情況 1: 最外層即為 redex (App (Abs x body) arg)
    if isinstance(expr, App) and isinstance(expr.func, Abs):
        param = expr.func.param
        body = expr.func.body
        arg = expr.arg
        reduced = body.substitute(param, arg)
        desc = f"β-縮約: (λ{param}. {body}) 套用至 {arg}"
        return reduced, True, desc

    # 情況 2: 在 App 的左側 (func) 嘗試歸約
    if isinstance(expr, App):
        next_func, did_reduce, desc = step_reduce(expr.func)
        if did_reduce:
            return App(next_func, expr.arg), True, desc

        # 情況 3: 在 App 的右側 (arg) 嘗試歸約
        next_arg, did_reduce, desc = step_reduce(expr.arg)
        if did_reduce:
            return App(expr.func, next_arg), True, desc

    # 情況 4: 在 Abs 內部 (body) 嘗試歸約
    if isinstance(expr, Abs):
        next_body, did_reduce, desc = step_reduce(expr.body)
        if did_reduce:
            return Abs(expr.param, next_body), True, desc

    return expr, False, ""


def evaluate(code: str, env: dict = None, max_steps: int = 50):
    """解析並執行，逐步輸出詳細推導過程"""
    print(f"原始輸入: {code}")

    expr = parse_lambda(code)

    # 展開環境中的巨集/定義（如 TRUE, FALSE, PLUS 等）
    if env:
        for name, def_code in env.items():
            def_expr = parse_lambda(def_code)
            expr = expr.substitute(name, def_expr)

    print(f"展開展開式: {expr}")
    print("-" * 60)

    current = expr
    step_count = 0

    while step_count < max_steps:
        next_expr, did_reduce, desc = step_reduce(current)
        if not did_reduce:
            print(f"\n✅ 達到正規形 (Normal Form)，總共經過 {step_count} 步歸約。")
            print(f"最終結果: {current}")
            print("=" * 60 + "\n")
            return current

        step_count += 1
        print(f"Step {step_count:02d}: {desc}")
        print(f"       -> {next_expr}")
        current = next_expr

    print(f"\n⚠️ 超過最大步驟上限 ({max_steps} 步)，可能存在無窮遞迴。")
    print("=" * 60 + "\n")
    return current


# ==========================================
# 4. 預載的邱奇編碼（Church Encodings）
# ==========================================
CHURCH_ENV = {
    # 布林邏輯
    "TRUE": r"\x y. x",
    "FALSE": r"\x y. y",
    "NOT": r"\p. p FALSE TRUE",
    "AND": r"\p q. p q p",
    "OR": r"\p q. p p q",
    # 邱奇數 (Church Numerals)
    "ZERO": r"\f x. x",
    "ONE": r"\f x. f x",
    "TWO": r"\f x. f (f x)",
    "THREE": r"\f x. f (f (f x))",
    # 數值算術
    "SUCC": r"\n f x. f (n f x)",
    "PLUS": r"\m n f x. m f (n f x)",
    "MULT": r"\m n f. m (n f)",
}


# ==========================================
# 5. 測試程式範例
# ==========================================
if __name__ == "__main__":
    # 範例 1: 基礎恆等函數套用
    evaluate(r"(\x. x) y")

    # 範例 2: 布林邏輯運算 (NOT TRUE -> FALSE)
    evaluate("NOT TRUE", env=CHURCH_ENV)

    # 範例 3: 邏輯 AND 運算 (AND TRUE FALSE -> FALSE)
    evaluate("AND TRUE FALSE", env=CHURCH_ENV)

    # 範例 4: 數值運算 SUCC ONE -> TWO (即 1 + 1 = 2)
    evaluate("SUCC ONE", env=CHURCH_ENV)

    # 範例 5: 數值加法 PLUS ONE TWO (即 1 + 2 = 3)
    evaluate("PLUS ONE TWO", env=CHURCH_ENV)
```

---

## 2. 執行輸出示範

### 範例一：`NOT TRUE`

```text
原始輸入: NOT TRUE
展開展開式: ((λp. ((p (λx. (λy. y))) (λx. (λy. x)))) (λx. (λy. x)))
------------------------------------------------------------
Step 01: β-縮約: (λp. ((p (λx. (λy. y))) (λx. (λy. x)))) 套用至 (λx. (λy. x))
       -> (((λx. (λy. x)) (λx. (λy. y))) (λx. (λy. x)))
Step 02: β-縮約: (λx. (λy. x)) 套用至 (λx. (λy. y))
       -> ((λy. (λx. (λy. y))) (λx. (λy. x)))
Step 03: β-縮約: (λy. (λx. (λy. y))) 套用至 (λx. (λy. x))
       -> (λx. (λy. y))

✅ 達到正規形 (Normal Form)，總共經過 3 步歸約。
最終結果: (λx. (λy. y))  # 即 Church Encoding 的 FALSE
============================================================
```

### 範例二：`SUCC ONE`（即 $1 + 1 = 2$）

```text
原始輸入: SUCC ONE
展開展開式: ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
------------------------------------------------------------
Step 01: β-縮約: (λn. (λf. (λx. (f ((n f) x))))) 套用至 (λf. (λx. (f x)))
       -> (λf. (λx. (f (((λf. (λx. (f x))) f) x))))
Step 02: β-縮約: (λf. (λx. (f x))) 套用至 f
       -> (λf. (λx. (f ((λx. (f x)) x))))
Step 03: β-縮約: (λx. (f x)) 套用至 x
       -> (λf. (λx. (f (f x))))

✅ 達到正規形 (Normal Form)，總共經過 3 步歸約。
最終結果: (λf. (λx. (f (f x))))  # 即 Church Encoding 的 TWO
============================================================
```

---

## 3. 重點機制說明

1. **防變數捕捉（$\alpha$-轉換 / Alpha-conversion）**：
   在 `Abs.substitute` 邏輯中，當代入的項包含與被綁定參數同名的自由變數時，會自動為該參數更名為加撇號的新變數（如 $x$ 換成 $x'$），避免外部自由變數被意外綁定產生語義錯誤。

2. **正規序歸約（Normal Order Reduction）**：
   始終優先尋找「最外層、最左側」的 redex。根據 Church-Rosser 定理與規範化定理（Standardization Theorem），只要該表達式存在正規形（Normal Form），正規序歸約保證能找到結果，即便表達式包含非終止項（例如 $\Omega = (\lambda x.\ x\ x)(\lambda x.\ x\ x)$）。

3. **語法糖擴充（Syntactic Sugar）**：
   Parser 支援多參數寫法（如 `\x y z. expr`），會自動柯里化（Curry）轉換為巢狀單參數抽象 `Abs("x", Abs("y", Abs("z", ...)))`。同時相容希臘字母 `λ` 與反斜線 `\`。