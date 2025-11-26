import re

# -------------------------
# 공통: { } 감싸기
# -------------------------
def wrap(s):
    s = s.strip()
    return s if (s.startswith("{") and s.endswith("}")) else f"{{{s}}}"

# -------------------------
# \frac
# -------------------------
def convert_frac(expr):
    pattern = r'\\frac\s*{(.*?)}\s*{(.*?)}'

    while True:
        m = re.search(pattern, expr)
        if not m:
            break
        a, b = wrap(m.group(1)), wrap(m.group(2))
        expr = expr.replace(m.group(0), f"{a} over {b}")
    return expr

# -------------------------
# sqrt
# -------------------------
def convert_sqrt(expr):
    # sqrt[n]{x}
    expr = re.sub(
        r'\\sqrt\s*\[(.+?)\]\s*{(.+?)}',
        lambda m: f"sqrt[{m.group(1)}] {wrap(m.group(2))}",
        expr,
    )
    # sqrt{x}
    expr = re.sub(
        r'\\sqrt\s*{(.+?)}',
        lambda m: f"sqrt {wrap(m.group(1))}",
        expr,
    )
    return expr

# -------------------------
# dot, ddot, bar, hat, vec
# -------------------------
def convert_accents(expr):
    table = {
        r'\\dot{(.+?)}': "dot",
        r'\\ddot{(.+?)}': "ddot",
        r'\\bar{(.+?)}': "bar",
        r'\\hat{(.+?)}': "hat",
        r'\\vec{(.+?)}': "vec",
    }
    for p, word in table.items():
        expr = re.sub(p, lambda m: f"{word} {wrap(m.group(1))}", expr)
    return expr

# -------------------------
# integral, sum
# -------------------------
def convert_op(op, expr):
    # \op_{a}^{b}
    expr = re.sub(
        rf'\\{op}_{{(.+?)}}\\^{{(.+?)}}',
        lambda m: f"{op} _{wrap(m.group(1))} ^{wrap(m.group(2))}",
        expr,
    )
    # 단독 \op
    expr = re.sub(rf'\\{op}', op, expr)
    return expr

# -------------------------
# matrix 류
# -------------------------
def convert_matrix(expr):

    def handle(kind, content):
        rows = content.replace("\\\\", "#")
        # 각 요소 감싸기
        rows = re.sub(r'([^&#]+)', lambda m: wrap(m.group(1)), rows)
        return f"{kind}{{{rows}}}"

    patterns = {
        'pmatrix': r'\\begin{pmatrix}(.*?)\\end{pmatrix}',
        'bmatrix': r'\\begin{bmatrix}(.*?)\\end{bmatrix}',
        'matrix':  r'\\begin{matrix}(.*?)\\end{matrix}',
    }

    for kind, pat in patterns.items():
        expr = re.sub(pat, lambda m: handle(kind, m.group(1)), expr, flags=re.S)
    return expr

# -------------------------
# 보정
# -------------------------
def fix_sup(expr):
    return re.sub(r'\^([A-Za-z0-9])', r'^{\1}', expr)

def fix_sub(expr):
    return re.sub(r'_([A-Za-z0-9])', r'_{\1}', expr)

def clean(expr):
    expr = expr.replace(r'\left', '')
    expr = expr.replace(r'\right', '')
    return expr

# -------------------------
# 그리스 문자 변경(수동으로 추가 가능)
# -------------------------
def convert_greek(expr):
    greek_table = {
        r'\alpha': 'alpha',
        r'\beta': 'beta',
        r'\gamma': 'gamma',
        r'\delta': 'delta',
        r'\epsilon': 'epsilon',
        r'\theta': 'theta',
        r'\lambda': 'lambda',
        r'\mu': 'mu',
        r'\nu': 'nu',
        r'\pi': 'pi',
        r'\rho': 'rho',
        r'\sigma': 'sigma',
        r'\phi': 'phi',
        r'\omega': 'omega',
    }
    for k, v in greek_table.items():
        expr = expr.replace(k, v)
    return expr

def convert_spaces(expr):
    return expr.replace(r'\,', '`') # latex에서 \,을 hwp에서 `으로 변경(반칸 띄기)

# -------------------------
# 메인
# -------------------------
def convert_latex_to_hwp(expr):
    expr = expr.strip()
    expr = clean(expr)
    expr = convert_matrix(expr)
    expr = convert_frac(expr)
    expr = convert_sqrt(expr)
    expr = convert_accents(expr)
    expr = convert_op("int", expr)
    expr = convert_op("sum", expr)    
    expr = convert_greek(expr)
    expr = convert_spaces(expr)
    expr = fix_sup(expr)
    expr = fix_sub(expr)
    return expr


# 수식 입력
if __name__ == "__main__":
    latex = r"""




P(v) = 4\pi \left( \frac{M}{2\pi R\,T} \right)^{3/2} v^2 e^{-Mv^2 / 2R\,T}




"""
print(convert_latex_to_hwp(latex))