#1. 主程式碼：
import sys
import itertools
from typing import List, Tuple, Optional

# 當變數數超過此門檻時，只計算結果，不列印逐行真值表，避免終端輸出卡死
MAX_VARS_TO_PRINT = 16


def parse_dimacs(file_content: str) -> Tuple[int, int, List[List[int]]]:
    """解析標準 DIMACS CNF 格式字串。

    返回: (變數數量, 子句數量, 子句列表)
    """
    clauses: List[List[int]] = []
    num_vars = 0
    num_clauses = 0
    current_clause: List[int] = []

    for line in file_content.splitlines():
        line = line.strip()
        if not line or line.startswith('c'):
            continue  # 忽略空行與註解行
        
        if line.startswith('p'):
            # 解析問題頭資訊：p cnf <vars> <clauses>
            parts = line.split()
            if len(parts) >= 4 and parts[1] == 'cnf':
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
            continue

        # 解析文字，每行以 0 結尾
        tokens = line.split()
        for token in tokens:
            lit = int(token)
            if lit == 0:
                clauses.append(current_clause)
                current_clause = []
            else:
                current_clause.append(lit)

    if current_clause:
        clauses.append(current_clause)

    return num_vars, num_clauses, clauses


def format_cnf_string(clauses: List[List[int]]) -> str:
    """將 CNF 子句轉化為直觀的布林表示字串 (x1 v ~x2) ^ ..."""
    if not clauses:
        return "T (Empty formula)"

    clause_strs = []
    for clause in clauses:
        if not clause:
            clause_strs.append("F")  # 空子句為 False
            continue
        lits = []
        for lit in clause:
            if lit > 0:
                lits.append(f"x{lit}")
            else:
                lits.append(f"~x{-lit}")
        clause_strs.append("(" + " v ".join(lits) + ")")

    return " ^ ".join(clause_strs)


def evaluate_formula(clauses: List[List[int]], assignment: List[bool]) -> bool:
    """評估給定賦值在 CNF 下的真值。

    assignment: 長度為 n 的布林列表，下標 0 對應變數 x1。
    """
    for clause in clauses:
        clause_satisfied = False
        for lit in clause:
            var_idx = abs(lit) - 1
            var_val = assignment[var_idx]
            # 若為正文字且值為 True，或負文字且值為 False，則該文字為真
            if (lit > 0 and var_val) or (lit < 0 and not var_val):
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False
    return True


def solve_sat(num_vars: int, num_clauses: int, clauses: List[List[int]]):
    """系統性枚舉 2^n 種賦值並輸出真值表與 SAT 結果。"""
    print(f"Variables: {num_vars}   Clauses: {len(clauses)}")
    print(f"Formula (CNF): {format_cnf_string(clauses)}\n")

    # 處理特殊情況：空子句必為 UNSAT
    has_empty_clause = any(len(c) == 0 for c in clauses)
    
    total_assignments = 2 ** num_vars
    satisfying_count = 0
    first_witness: Optional[List[bool]] = None

    should_print_table = num_vars <= MAX_VARS_TO_PRINT

    if should_print_table:
        header_vars = " ".join([f"x{i}" for i in range(1, num_vars + 1)])
        print(f"{header_vars} | F")
        print("-" * (len(header_vars) + 4))

    # 系統性枚舉所有賦值（從 False 到 True）
    for bits in itertools.product([False, True], repeat=num_vars):
        assignment = list(bits)
        is_sat = (not has_empty_clause) and evaluate_formula(clauses, assignment)

        if is_sat:
            satisfying_count += 1
            if first_witness is None:
                first_witness = assignment

        if should_print_table:
            row_vals = "  ".join(["T" if b else "F" for b in assignment])
            # 右側對齊格式化
            print(f" {row_vals} | {1 if is_sat else 0}")

    if not should_print_table:
        print(f"(Truth table omitted: n = {num_vars} > {MAX_VARS_TO_PRINT})")

    print("-" * 30)
    print(f"Enumerated {total_assignments} assignment(s); {satisfying_count} satisfy the formula.")

    if satisfying_count > 0 and first_witness is not None:
        witness_str = " ".join([f"x{i}={'T' if val else 'F'}" for i, val in enumerate(first_witness, 1)])
        print("Result: SATISFIABLE")
        print(f"  A satisfying assignment: {witness_str}")
    else:
        print("Result: UNSATISFIABLE")


def run_demos():
    """內建 Demo：展示一個可滿足與一個不可滿足的公式。"""
    print("=== Demo 1: Satisfiable Example ===")
    demo_sat_cnf = """c Demo Satisfiable Formula
p cnf 3 3
1 -3 0
2 3 -1 0
-2 3 0
"""
    v, c, clauses = parse_dimacs(demo_sat_cnf)
    solve_sat(v, c, clauses)

    print("\n" + "=" * 45 + "\n")

    print("=== Demo 2: Unsatisfiable Example ===")
    # (x1) ^ (~x1) 矛盾式
    demo_unsat_cnf = """c Demo Unsatisfiable Formula
p cnf 1 2
1 0
-1 0
"""
    v, c, clauses = parse_dimacs(demo_unsat_cnf)
    solve_sat(v, c, clauses)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            v, c, clauses = parse_dimacs(content)
            solve_sat(v, c, clauses)
        except FileNotFoundError:
            print(f"Error: 找不到檔案 {file_path}")
            sys.exit(1)
    else:
        run_demos()