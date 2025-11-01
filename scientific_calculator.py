import streamlit as st
import numpy as np # Used for scientific functions like sin, cos, log
import math
import re

# --- State Management & Logic ---
if 'expression' not in st.session_state:
    st.session_state.expression = ""
if 'result' not in st.session_state:
    st.session_state.result = ""

def calculate():
    """Evaluates the mathematical expression using Python's eval (with safety)."""
    try:
        # Replace calculator notation with Python's math/numpy syntax
        safe_expression = st.session_state.expression.replace('^', '**')
        
        # Use a restricted namespace for security (only allow math and numpy functions)
        allowed_functions = {
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'sqrt': math.sqrt, 'log': np.log10, 'ln': np.log, 
            'pi': np.pi, 'e': np.e
        }
        
        # NOTE: eval() is powerful but dangerous. A more robust solution would use a library 
        # like 'sympy' or a dedicated expression parser.
        final_result = str(eval(safe_expression, {"__builtins__": None}, allowed_functions))
        st.session_state.result = final_result
        st.session_state.expression = final_result # Continue calculation from result
        
    except Exception as e:
        st.session_state.result = "Error"
        st.session_state.expression = ""

def update_expression(key):
    """Appends the pressed key to the current expression."""
    if st.session_state.result == "Error":
        st.session_state.expression = ""
        st.session_state.result = ""

    if key == 'AC':
        st.session_state.expression = ""
        st.session_state.result = ""
    elif key == 'DEL':
        st.session_state.expression = st.session_state.expression[:-1]
    elif key == '=':
        calculate()
    else:
        st.session_state.expression += str(key)

# --- Streamlit UI Components ---
st.set_page_config(page_title="Scientific Calculator", layout="centered")
st.title("🧮 Streamlit Scientific Calculator")
st.markdown("---")

# Display Screen (mimicking the two-line Casio display)
st.container(border=True, height=100)
st.write(f'<p style="font-size: 14px; color: grey; text-align: right; margin: 0px;">{st.session_state.expression}</p>', unsafe_allow_html=True)
st.write(f'<h3 style="text-align: right; margin: 0px;">{st.session_state.result}</h3>', unsafe_allow_html=True)
st.markdown("---")

# Calculator Buttons Layout (5 columns to mimic Casio's width)
# Define the button grid
button_rows = [
    ['AC', 'DEL', '(', ')', '/'],
    ['sin(', 'cos(', 'tan(', '^', '*'],
    ['sqrt(', 'log(', 'ln(', 'pi', '-'],
    ['7', '8', '9', 'e', '+'],
    ['4', '5', '6', '.', 'Ans'],
    ['1', '2', '3', '0', '=']
]

for row in button_rows:
    cols = st.columns(5)
    for i, button_label in enumerate(row):
        # Different styles for AC/DEL and equals button
        if button_label in ('AC', 'DEL'):
            style = "warning"
        elif button_label == '=':
            style = "primary"
        else:
            style = "secondary"

        with cols[i]:
            st.button(
                button_label, 
                key=button_label, 
                on_click=update_expression, 
                args=[button_label],
                use_container_width=True,
                type=style
            )
