import streamlit as st
import math
from math import pi, e

# --- Helper: safe eval environment ---
SAFE_FUNCS = {
    'sin': lambda x, mode='rad': math.sin(math.radians(x)) if mode == 'deg' else math.sin(x),
    'cos': lambda x, mode='rad': math.cos(math.radians(x)) if mode == 'deg' else math.cos(x),
    'tan': lambda x, mode='rad': math.tan(math.radians(x)) if mode == 'deg' else math.tan(x),
    'asin': lambda x, mode='rad': math.degrees(math.asin(x)) if mode == 'deg' else math.asin(x),
    'acos': lambda x, mode='rad': math.degrees(math.acos(x)) if mode == 'deg' else math.acos(x),
    'atan': lambda x, mode='rad': math.degrees(math.atan(x)) if mode == 'deg' else math.atan(x),
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

# constants
CONSTS = {'pi': pi, 'e': e}

# Build safe namespace for eval
def build_safe_namespace(mode='rad'):
    ns = {**SAFE_FUNCS, **CONSTS, '__builtins__': None}
    # wrap trig functions to capture degree/radian mode
    ns['sin'] = lambda x: SAFE_FUNCS['sin'](x, mode)
    ns['cos'] = lambda x: SAFE_FUNCS['cos'](x, mode)
    ns['tan'] = lambda x: SAFE_FUNCS['tan'](x, mode)
    ns['asin'] = lambda x: SAFE_FUNCS['asin'](x, mode)
    ns['acos'] = lambda x: SAFE_FUNCS['acos'](x, mode)
    ns['atan'] = lambda x: SAFE_FUNCS['atan'](x, mode)
    return ns

# Evaluate expression safely
def safe_eval(expr: str, mode='rad'):
    # replace common visual operators
    expr = expr.replace('^', '**')
    # don't allow double-underscores
    if '__' in expr:
        raise ValueError('Invalid expression')
    ns = build_safe_namespace(mode)
    # limit characters: allow digits, letters, operators, parentheses, dot, spaces
    allowed_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/()., _^"
    for ch in expr:
        if ch not in allowed_chars:
            raise ValueError(f'Invalid character: {ch}')
    return eval(expr, {}, ns)

# --- Streamlit App ---
st.set_page_config(page_title="Casio-Style Scientific Calculator", layout="wide")

# Simple CSS to make it look calculator-like
st.markdown(
    """
    <style>
    .calculator {max-width: 480px; margin: auto;}
    .display {background: #1f2937; color: #fff; padding: 18px; border-radius: 8px; font-size: 26px; font-family: 'Courier New', monospace;}
    .btn {width: 64px; height: 48px; margin: 6px 6px; border-radius: 8px; font-size: 16px;}
    .btn-op {background: #f97316; color: #fff;}
    .btn-func {background: #6b7280; color: #fff;}
    .btn-num {background: #e5e7eb;}
    .small {width: 46px; height: 40px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Casio‑style Scientific Calculator 🧮")

# session state
if 'expr' not in st.session_state:
    st.session_state.expr = ''
if 'mode' not in st.session_state:
    st.session_state.mode = 'deg'  # default to degrees like many calculators
if 'memory' not in st.session_state:
    st.session_state.memory = 0.0
if 'result' not in st.session_state:
    st.session_state.result = ''

# Top controls
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button('DEG' if st.session_state.mode == 'deg' else 'RAD'):
        st.session_state.mode = 'rad' if st.session_state.mode == 'deg' else 'deg'
with col2:
    if st.button('MC'):
        st.session_state.memory = 0.0
    if st.button('MR'):
        st.session_state.expr += str(st.session_state.memory)
with col3:
    st.checkbox('Show history (last result)', value=True, key='show_hist')

# Display
st.markdown(f"<div class='calculator'><div class='display'>{st.session_state.expr or '0'}</div></div>", unsafe_allow_html=True)

# Button grid layout using columns
btn_rows = []

# helper to add button onclick
def btn_press(val):
    st.session_state.expr = st.session_state.expr + str(val)

def clear():
    st.session_state.expr = ''
    st.session_state.result = ''

def backspace():
    st.session_state.expr = st.session_state.expr[:-1]

def evaluate():
    try:
        res = safe_eval(st.session_state.expr, st.session_state.mode)
        # format small floats
        if isinstance(res, float):
            # avoid scientific until necessary
            st.session_state.result = str(round(res, 12)).rstrip('0').rstrip('.') if abs(res) < 1e12 else f"{res:.6e}"
        else:
            st.session_state.result = str(res)
        st.session_state.expr = st.session_state.result
        return
    except Exception as e:
        st.session_state.result = 'Error'
        st.session_state.expr = ''

# Row 1: functions
r1 = st.columns([1,1,1,1,1])
if r1[0].button('AC'):
    clear()
if r1[1].button('DEL'):
    backspace()
if r1[2].button('%'):
    btn_press('/100')
if r1[3].button('('):
    btn_press('(')
if r1[4].button(')'):
    btn_press(')')

# Row 2
r2 = st.columns([1,1,1,1,1])
if r2[0].button('sin'):
    btn_press('sin(')
if r2[1].button('cos'):
    btn_press('cos(')
if r2[2].button('tan'):
    btn_press('tan(')
if r2[3].button('^'):
    btn_press('**')
if r2[4].button('√'):
    btn_press('sqrt(')

# Row 3
r3 = st.columns([1,1,1,1,1])
if r3[0].button('ln'):
    btn_press('ln(')
if r3[1].button('log'):
    btn_press('log(')
if r3[2].button('π'):
    btn_press('pi')
if r3[3].button('e'):
    btn_press('e')
if r3[4].button('!'):
    btn_press('factorial(')

# Row 4: digits 7 8 9 /
r4 = st.columns([1,1,1,1])
if r4[0].button('7'):
    btn_press('7')
if r4[1].button('8'):
    btn_press('8')
if r4[2].button('9'):
    btn_press('9')
if r4[3].button('÷'):
    btn_press('/')

# Row 5: 4 5 6 *
r5 = st.columns([1,1,1,1])
if r5[0].button('4'):
    btn_press('4')
if r5[1].button('5'):
    btn_press('5')
if r5[2].button('6'):
    btn_press('6')
if r5[3].button('×'):
    btn_press('*')

# Row 6: 1 2 3 -
r6 = st.columns([1,1,1,1])
if r6[0].button('1'):
    btn_press('1')
if r6[1].button('2'):
    btn_press('2')
if r6[2].button('3'):
    btn_press('3')
if r6[3].button('−'):
    btn_press('-')

# Row 7: 0 . +/- +
r7 = st.columns([1,1,1,1])
if r7[0].button('0'):
    btn_press('0')
if r7[1].button('.'):
    btn_press('.')
if r7[2].button('+/-'):
    # toggle sign: naive approach
    expr = st.session_state.expr
    if expr.startswith('-'):
        st.session_state.expr = expr[1:]
    else:
        st.session_state.expr = '-' + expr
if r7[3].button('+'):
    btn_press('+')

# Bottom row: memory +/- and equals
rb = st.columns([1,1,2,2])
if rb[0].button('M+'):
    # try to add current value to memory
    try:
        val = float(st.session_state.expr) if st.session_state.expr else 0.0
    except:
        val = 0.0
    st.session_state.memory += val
if rb[1].button('M-'):
    try:
        val = float(st.session_state.expr) if st.session_state.expr else 0.0
    except:
        val = 0.0
    st.session_state.memory -= val
if rb[2].button('Ans'):
    if st.session_state.result:
        st.session_state.expr += str(st.session_state.result)
if rb[3].button('='):
    evaluate()

# Show result / history
st.write('')
res_col, hist_col = st.columns([2,1])
with res_col:
    st.subheader('Result')
    st.text(st.session_state.result or '—')
with hist_col:
    st.subheader('Mode')
    st.write(st.session_state.mode.upper())
    st.subheader('Memory')
    st.write(st.session_state.memory)

# Footer instructions
st.caption('Looks similar to a Casio 991 — use the buttons to build expressions. Trig uses DEG by default. Supports: sin, cos, tan, asin, acos, atan, ln, log, sqrt, factorial, pow (^ -> use ^ or **).')
