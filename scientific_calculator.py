import streamlit as st
import math
from math import pi, e

# --- Safe evaluation ---
SAFE_FUNCS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sqrt': math.sqrt,
    'log': lambda x: math.log10(x),
    'ln': math.log,
    'pow': pow,
    'exp': math.exp,
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
    'factorial': math.factorial,
}
CONSTS = {'pi': pi, 'e': e}

def build_safe_namespace(mode='rad'):
    # wrap trig to respect deg/rad
    def wrap(f):
        return (lambda x: f(math.radians(x))) if mode == 'deg' else f

    ns = {**SAFE_FUNCS, **CONSTS, '__builtins__': None}
    ns['sin'] = wrap(math.sin)
    ns['cos'] = wrap(math.cos)
    ns['tan'] = wrap(math.tan)
    ns['asin'] = (lambda x: math.degrees(math.asin(x))) if mode == 'deg' else math.asin
    ns['acos'] = (lambda x: math.degrees(math.acos(x))) if mode == 'deg' else math.acos
    ns['atan'] = (lambda x: math.degrees(math.atan(x))) if mode == 'deg' else math.atan
    ns['sqrt'] = math.sqrt
    ns['ln'] = math.log
    ns['log'] = lambda x: math.log10(x)
    ns['pi'] = pi
    ns['e'] = e
    return ns

def safe_eval(expr: str, mode='rad'):
    expr = expr.replace('^', '**').replace('×', '*').replace('÷', '/')
    if '__' in expr:
        raise ValueError('Invalid expression')
    allowed = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/()., _^""'
    for ch in expr:
        if ch not in allowed:
            raise ValueError(f'Invalid character: {ch}')
    ns = build_safe_namespace(mode)
    return eval(expr, {}, ns)

# --- Streamlit UI ---
st.set_page_config(page_title="Casio 991FX-like Scientific Calculator", layout="wide")

# CSS mimic of Casio 991FX
st.markdown('''
<style>
body {background: #0f172a}
.calculator {max-width: 560px; margin: 18px auto; background: linear-gradient(180deg,#111827,#0b1220); padding: 14px; border-radius: 12px; box-shadow: 0 8px 30px rgba(2,6,23,.8);}
.display-top {background: #0b1220; color: #a5b4fc; padding: 10px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 14px;}
.display-main {background: #e6eef8; color: #0b1220; padding: 12px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 28px; text-align: right;}
.row {display:flex; gap:8px; margin-top:8px}
.btn {flex:1; padding:10px 6px; border-radius:6px; border:none; font-weight:600; cursor:pointer}
.btn-num{background:#f8fafc}
.btn-op{background:#f97316; color:white}
.btn-func{background:#374151; color:white}
.btn-shift{background:#fde68a}
.btn-eq{background:#06b6d4; color:white; flex:2}
.small{flex:0.8}
</style>
''', unsafe_allow_html=True)

st.markdown("""<div class='calculator'>""", unsafe_allow_html=True)
st.title("Casio 991FX — Streamlit Edition")

# session state initialization
if 'expr' not in st.session_state:
    st.session_state.expr = ''
if 'result' not in st.session_state:
    st.session_state.result = ''
if 'mode' not in st.session_state:
    st.session_state.mode = 'deg'  # typical calculator default
if 'memory' not in st.session_state:
    st.session_state.memory = 0.0
if 'shift' not in st.session_state:
    st.session_state.shift = False

# Top display (two-line like CASIO)
st.markdown(f"<div class='display-top'>Mode: <b>{st.session_state.mode.upper()}</b> &nbsp;&nbsp; Shift: <b>{'ON' if st.session_state.shift else 'OFF'}</b></div>", unsafe_allow_html=True)
st.markdown(f"<div class='display-main'>{st.session_state.expr or st.session_state.result or '0'}</div>", unsafe_allow_html=True)

# helper actions
def press(s):
    st.session_state.expr += str(s)
    st.session_state.shift = False

def clear_all():
    st.session_state.expr = ''
    st.session_state.result = ''
    st.session_state.shift = False

def backspace():
    st.session_state.expr = st.session_state.expr[:-1]
    st.session_state.shift = False

def calculate():
    try:
        res = safe_eval(st.session_state.expr, st.session_state.mode)
        if isinstance(res, float):
            st.session_state.result = (str(round(res, 12)).rstrip('0').rstrip('.'))
        else:
            st.session_state.result = str(res)
        st.session_state.expr = st.session_state.result
    except Exception as e:
        st.session_state.result = 'Error'
        st.session_state.expr = ''

# Row helpers to create UI buttons using columns
cols = st.columns(5)
with cols[0]:
    if st.button('SHIFT', key='shift', help='Toggle shift'):
        st.session_state.shift = not st.session_state.shift
with cols[1]:
    if st.button('ALPHA', key='alpha'):
        # ALPHA could be used for variable names; for now toggle shift as placeholder
        st.session_state.shift = not st.session_state.shift
with cols[2]:
    if st.button('MODE'):
        st.session_state.mode = 'rad' if st.session_state.mode == 'deg' else 'deg'
with cols[3]:
    if st.button('ON/AC'):
        clear_all()
with cols[4]:
    if st.button('Del'):
        backspace()

# Second row: memory & stats
r2 = st.columns(5)
if r2[0].button('x^2' if not st.session_state.shift else 'x^3'):
    if st.session_state.shift:
        press('**3')
    else:
        press('**2')
if r2[1].button('x^y' if not st.session_state.shift else '√'):
    if st.session_state.shift:
        press('sqrt(')
    else:
        press('**')
if r2[2].button('log' if not st.session_state.shift else 'ln'):
    press('log(' if not st.session_state.shift else 'ln(')
if r2[3].button('ENG' if not st.session_state.shift else 'EXP'):
    press('e*' if st.session_state.shift else '10**')
if r2[4].button('%'):
    press('/100')

# Third row: trig functions
r3 = st.columns(5)
if r3[0].button('sin' if not st.session_state.shift else 'sin⁻¹'):
    press('asin(' if st.session_state.shift else 'sin(')
if r3[1].button('cos' if not st.session_state.shift else 'cos⁻¹'):
    press('acos(' if st.session_state.shift else 'cos(')
if r3[2].button('tan' if not st.session_state.shift else 'tan⁻¹'):
    press('atan(' if st.session_state.shift else 'tan(')
if r3[3].button('(-)' ):
    # +/- toggle
    expr = st.session_state.expr
    if expr.startswith('-'):
        st.session_state.expr = expr[1:]
    else:
        st.session_state.expr = '-' + expr
if r3[4].button('π'):
    press('pi')

# Fourth row: functions
r4 = st.columns(5)
if r4[0].button('ln' if not st.session_state.shift else 'e^x'):
    press('ln(' if not st.session_state.shift else 'exp(')
if r4[1].button('ANS'):
    press(st.session_state.result or '')
if r4[2].button('('):
    press('(')
if r4[3].button(')'):
    press(')')
if r4[4].button('!'):
    press('factorial(')

# Digit keypad layout (rows of 3 + operator)
for digits, op in [(['7','8','9'],'÷'), (['4','5','6'],'×'), (['1','2','3'],'−'), (['0','.','EXP'],'+')]:
    cols = st.columns([1,1,1,1])
    for i, d in enumerate(digits):
        if cols[i].button(d):
            if d == 'EXP':
                press('e')
            else:
                press(d)
    if cols[3].button(op):
        press('/' if op == '÷' else '*' if op == '×' else '-' if op == '−' else '+')

# Bottom row: memory and equals
bcols = st.columns(4)
if bcols[0].button('M+'):
    try:
        val = float(st.session_state.expr) if st.session_state.expr else 0.0
    except:
        val = 0.0
    st.session_state.memory += val
if bcols[1].button('M-'):
    try:
        val = float(st.session_state.expr) if st.session_state.expr else 0.0
    except:
        val = 0.0
    st.session_state.memory -= val
if bcols[2].button('MR'):
    press(str(st.session_state.memory))
if bcols[3].button('='):
    calculate()

# Footer info
st.markdown('</div>', unsafe_allow_html=True)
st.write('')
st.caption('Design inspired by Casio fx-991 series. SHIFT toggles alternate functions for several keys. Trig honors DEG/RAD mode. For keyboard support or exact visual matching, I can add custom CSS and JS integration.')

