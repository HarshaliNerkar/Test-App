import streamlit as st
import numpy as np
import math

# --- Safe Evaluation Logic (Unchanged for Functionality) ---

def safe_eval(expression):
    """
    Safely evaluates a string expression with scientific functions.
    Handles 'Ans', 'log_b', '!', and other user-friendly notations.
    """
    expression = expression.replace('^', '**')
    
    if 'Ans' in expression and 'last_result' in st.session_state:
        expression = expression.replace('Ans', str(st.session_state.last_result))
    
    while '!' in expression:
        try:
            bang_index = expression.rfind('!')
            if bang_index == -1: break 

            base_start = bang_index - 1
            if base_start < 0: return "Syntax Error (Factorial)"

            if expression[base_start] == ')':
                open_paren_count = 1
                base_end = base_start
                while open_paren_count > 0 and base_end > 0:
                    base_end -= 1
                    if expression[base_end] == ')': open_paren_count += 1
                    elif expression[base_end] == '(': open_paren_count -= 1
                if open_paren_count != 0: return "Syntax Error (Factorial)"
                base_val = expression[base_end:base_start+1]
                replace_start = base_end
            else:
                while base_start >= 0 and (expression[base_start].isdigit() or expression[base_start] == '.'):
                    base_start -= 1
                base_start += 1 
                base_val = expression[base_start:bang_index]
                replace_start = base_start

            factorial_calc = f"math.factorial(int({base_val}))" 
            expression = expression[:replace_start] + factorial_calc + expression[bang_index+1:]

        except Exception:
            return "Syntax Error (Factorial)"
    
    expression = expression.replace('log_b(', 'math.log(')
    
    safe_dict = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'log': np.log10, 'ln': np.log, 
        'sqrt': np.sqrt, 'exp': np.exp,
        'Abs': abs, 'pi': np.pi, 'e': np.e,
        'math': math, '__builtins__': None
    }
    
    try:
        expression = expression.replace('pi', str(np.pi)).replace('e', str(np.e))
        result = eval(expression, {"__builtins__": None}, safe_dict)
        
        if isinstance(result, (float, np.float64)) and (abs(result) > 1e12 or (abs(result) < 1e-6 and abs(result) != 0)):
             return f"{result:.4e}"
        
        return str(result)
    except Exception:
        return "Syntax Error"

# --- State Management & Button Handlers (Unchanged) ---

if 'display' not in st.session_state:
    st.session_state.display = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = 0.0
if 'memory' not in st.session_state:
    st.session_state.memory = 0.0

def handle_button_press(key):
    current_display = st.session_state.display
    
    if key == 'AC':
        st.session_state.display = ""
        st.session_state.last_result = 0.0
        st.session_state.memory = 0.0 
    elif key == 'DEL':
        st.session_state.display = current_display[:-1]
    elif key == '=':
        result = safe_eval(current_display)
        st.session_state.display = result
        try:
            st.session_state.last_result = float(result)
        except ValueError:
            st.session_state.last_result = 0.0
            
    elif key == 'Ans':
        st.session_state.display += str(st.session_state.last_result)
        
    elif key == 'M+':
        try:
            value_to_add = float(safe_eval(current_display))
            st.session_state.memory += value_to_add
            st.session_state.display = f"M+ {value_to_add:.2f}" 
        except Exception:
            st.session_state.display = "M+ Error"
    elif key == 'MR':
        st.session_state.display += str(st.session_state.memory)
        
    else:
        if key in ('sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'exp', 'Abs', 'log_b'):
            st.session_state.display += f"{key}("
        else:
            st.session_state.display += key

# --- Streamlit UI with Black Background and White Buttons ---

st.set_page_config(page_title="High-Contrast Scientific Calculator", layout="centered")

# Inject custom CSS for Dark Mode styling with White Buttons
st.markdown(
    """
    <style>
    /* 1. Main app background: Black */
    .stApp {
        background-color: #000000; 
    }
    /* 2. Text and Title Colors: White */
    .stApp, h1, h2, h3, h4, .stCaption {
        color: #f0f0f0 !important;
    }
    /* 3. Button Styling: WHITE buttons with DARK text */
    .stButton > button {
        background-color: #FFFFFF; /* White button surface */
        color: #333333; /* Dark Grey/Black text for numbers and functions */
        border: 1px solid #CCCCCC; 
        font-weight: bold;
        font-size: 1.1em;
        border-radius: 5px;
        transition: background-color 0.1s, color 0.1s;
        box-shadow: 0 3px #AAAAAA; /* 3D shadow effect */
    }
    .stButton > button:hover {
        background-color: #EEEEEE; /* Slight grey on hover */
        box-shadow: 0 1px #AAAAAA; 
        transform: translateY(2px);
    }
    /* Primary buttons (AC, =, DEL) - Use a distinct color for text */
    .stButton > button[data-testid="stButton-primary"] {
        background-color: #FFFFFF; /* Keep background white */
        color: #FF4B4B; /* Red text for AC/DEL/Utility */
        border: 1px solid #FF4B4B; 
    }
    .stButton > button[data-testid="stButton-primary"]:hover {
        background-color: #EEEEEE;
        color: #CC0000;
    }

    /* 4. Display Screen Styling (LCD Look) */
    .stContainer {
        background-color: #e0e0e0; /* Off-white LCD look */
        border-radius: 10px;
        padding: 15px 10px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5); /* Inner shadow for depth */
        border: 2px solid #555555;
    }
    /* Display Text inside the container */
    .display-text {
        text-align: right; 
        overflow-x: auto; 
        font-family: 'Courier New', monospace; 
        font-size: 28px; 
        font-weight: bold; 
        color: #333333; /* Dark text on light background */
        height: 30px;
    }
    /* Remove default Streamlit padding from main content to maximize calculator size */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔳 Scientific Calculator (High Contrast)")
st.caption(f"Memory (M): **{st.session_state.memory:.2f}** | Last Answer (Ans): **{st.session_state.last_result:.2f}**")
st.markdown("---")

# --- Display Screen ---
with st.container(border=True, height=100):
    st.markdown(
        f"""
        <div class="display-text">
            {st.session_state.display if st.session_state.display else '0'}
        </div>
        """, 
        unsafe_allow_html=True
    )
st.markdown("---")


# --- Button Grid ---
button_rows = [
    ['Abs', 'log_b(', '!', 'M+', 'MR'],
    ['sin', 'cos', 'tan', '1/x', 'DEL'],
    ['log', 'ln', 'exp', 'sqrt', 'AC'],
    ['pi', '7', '8', '9', '/'],
    ['e', '4', '5', '6', '*'],
    ['^', '1', '2', '3', '-'],
    ['(', '0', '.', 'Ans', '+'],
    [')', '00', ' ', ' ', '='] 
]

unique_key_counter = 0

for row_index, row in enumerate(button_rows):
    cols = st.columns(len(row))
    for col_index, button_label in enumerate(row):
        
        # Use 'primary' for utility keys like AC, DEL, and = to apply the distinct red text style
        if button_label in ('AC', '=', 'DEL', 'M+', 'MR', 'Ans'):
            btn_type = "primary" 
        else:
            btn_type = "secondary"
            
        unique_key = f"btn_{button_label}_{unique_key_counter}" 
        unique_key_counter += 1
        
        if button_label == ' ':
            with cols[col_index]:
                 st.markdown(" ") 
            continue
            
        with cols[col_index]:
            st.button(
                button_label, 
                key=unique_key,  
                on_click=handle_button_press, 
                args=[button_label],
                use_container_width=True,
                type=btn_type
            )
