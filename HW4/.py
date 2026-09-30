#3. Python 程式實作
def babylonian_sqrt(S, initial_guess=2.0, tol=1e-7, max_iter=20):
    x = initial_guess
    print(f"k = 0: x = {x:.8f}")

    for k in range(1, max_iter + 1):
        x_next = 0.5 * (x + S / x)
        print(f"k = {k}: x = {x_next:.8f}, 誤差 = {abs(x_next - x):.2e}")

        if abs(x_next - x) < tol:
            return x_next
        x = x_next

    return x


# 求解 sqrt(5)
ans = babylonian_sqrt(S=5, initial_guess=2.0)
print(f"\n最終求得近似值: {ans:.8f}")