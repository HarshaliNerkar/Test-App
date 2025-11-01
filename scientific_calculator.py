import streamlit as st
import numpy as np
import math

# --- Safe Evaluation Logic ---

def safe_eval(expression):
    """
    Safely evaluates a string expression with scientific functions.
    Handles the common 'ans' and replaces user-friendly notation (^, sin, log)
    with Python/NumPy syntax.
    """
    # 1. Standardize the expression for Python
    expression = expression.replace('^', '**')
    
    # 2. Replace 'Ans' with the last result
    if 'Ans' in expression and 'last_result' in st.session_state:
        # Use str(st.session_state.last_result) to ensure it's a string for replacement
        expression = expression.replace('Ans', str(st.session_state.last_result))

    # 3. Define the safe namespace
    safe_dict = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'log': np.log10, 'ln': np.log, 
        'sqrt': np.sqrt, 'exp': np.exp,
        'pi': np.pi, 'e': np.e,
        # Allow basic arithmetic operations
        '__builtins__': None
    }
    
    # 4. Attempt evaluation
    try:
        # Evaluate the expression using the restricted namespace
        result = eval(expression, {"__builtins__": None}, safe_dict)
        return str(result)
    except Exception:
        return "Syntax Error"

# --- State Management ---

if 'display' not in st.session_state:
    st.session_state.display = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = 0.0

# --- Button Handlers ---

def handle_button_press(key):
    """Updates the display based on the button pressed."""
    
    current_display = st.session_state.display
    
    if key == 'AC':
        st.session_state.display = ""
        st.session_state.last_result = 0.0
    elif key == 'DEL':
        st.session_state.display = current_display[:-1]
    elif key == '=':
        # Evaluate and update the state
        result = safe_eval(current_display)
        st.session_state.display = result
        
        # Only save a valid result as 'last_result' (Ans)
        try:
            st.session_state.last_result = float(result)
        except ValueError:
            st.session_state.last_result = 0.0
            
    elif key == 'Ans':
        # Append the last result to the current display
        st.session_state.display += str(st.session_state.last_result)
        
    else:
        st.session_state.display += key

# --- Streamlit UI ---

st.set_page_config(page_title="Casio 991 Style Sci Calculator", layout="centered")
st.title("🔬 Scientific Calculator")
st.caption("Structured like a Casio fx-991, built with Streamlit")

# --- Display Screen ---
# Use an empty markdown/text placeholder to simulate a single display box
st.container(border=True, height=100)
st.markdown(
    f"""
    <div style="text-align: right; overflow-x: auto; font-size: 18px; color: grey;">
        {st.session_state.display}
    </div>
    <div style="text-align: right; font-size: 28px; font-weight: bold; height: 30px;">
        {st.session_state.display if st.session_state.display else '0'}
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("---")


# --- Button Grid (5x5 layout to mimic Casio) ---
button_rows = [
    # Row 1: Function Keys
    ['sin(', 'cos(', 'tan(', '^', 'sqrt('],
    # Row 2: Scientific & Constants
    ['log(', 'ln(', 'exp(', 'pi', 'e'],
    # Row 3: Utility & Division
    ['AC', 'DEL', '(', ')', '/'],
    # Row 4: Numbers & Operators
    ['7', '8', '9', '*', '-'],
    # Row 5: Numbers & Equals
    ['4', '5', '6', '+', '='],
    # Row 6: Bottom Row
    ['1', '2', '3', 'Ans', '.'],
    ['0', '00', '(', ')', '='] # Adjusted to fit 5 columns, last two are extra '='
]

for row in button_rows:
    # Use st.columns(5) for a typical scientific calculator width
    cols = st.columns(len(row))
    for i, button_label in enumerate(row):
        # Apply visual styling based on the button type
        if button_label in ('AC', 'DEL'):
            btn_type = "primary" # Orange/Red color for AC/DEL
        elif button_label == '=':
            btn_type = "primary"
        elif button_label in ('+', '-', '*', '/', '^'):
            btn_type = "secondary" # Grey/Darker buttons for operators
        else:
            btn_type = "secondary" # Default for numbers/functions
            
        with cols[i]:
            # The key must be unique, the on_click function passes the label to the handler
            st.button(
                button_label, 
                key=f"btn_{button_label}_{i}", 
                on_click=handle_button_press, 
                args=[button_label],
                use_container_width=True,
                type=btn_type
            )
