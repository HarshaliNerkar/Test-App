import streamlit as st
import numpy as np
import math

# --- Safe Evaluation Logic ---

def safe_eval(expression):
    """
    Safely evaluates a string expression with scientific functions.
    Handles 'Ans', 'log_b', '!', and other user-friendly notations.
    """
    # 1. Standardize the expression for Python
    expression = expression.replace('^', '**')
    
    # 2. Replace 'Ans' with the last result
    if 'Ans' in expression and 'last_result' in st.session_state:
        expression = expression.replace('Ans', str(st.session_state.last_result))
    
    # 3. Handle Factorial (needs special treatment as it's not a standard function)
    while '!' in expression:
        try:
            # Look for a number (or parenthesized expression) immediately before '!'
            # Find the last occurrence of '!'
            bang_index = expression.rfind('!')
            if bang_index == -1: break # No '!' found, exit loop

            # Find the start of the number or expression before '!'
            base_start = bang_index - 1
            if base_start < 0: return "Syntax Error (Factorial)"

            # Handle parenthesized expression before '!'
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
                # Handle numeric base
                while base_start >= 0 and (expression[base_start].isdigit() or expression[base_start] == '.'):
                    base_start -= 1
                base_start += 1 # Adjust to the start of the number
                base_val = expression[base_start:bang_index]
                replace_start = base_start

            factorial_calc = f"math.factorial(int({base_val}))" # Factorial works on integers
            expression = expression[:replace_start] + factorial_calc + expression[bang_index+1:]

        except Exception:
            return "Syntax Error (Factorial)"
    
    # 4. Handle log_base(x,b) -> math.log(x,b)
    expression = expression.replace('log_b(', 'math.log(')
    
    # 5. Define the safe namespace
    safe_dict = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'log': np.log10, 'ln': np.log, 
        'sqrt': np.sqrt, 'exp': np.exp,
        'Abs': abs, # Absolute value
        'pi': np.pi, 'e': np.e,
        'math': math, # For factorial and log with base
        '__builtins__': None
    }
    
    # 6. Attempt evaluation
    try:
        # Convert any remaining function syntax to the Python equivalent (e.g., 'sin(' to 'sin(')
        # We need to explicitly convert string pi/e constants to their float values if they weren't part of an eval()
        expression = expression.replace('pi', str(np.pi)).replace('e', str(np.e))
        
        result = eval(expression, {"__builtins__": None}, safe_dict)
        
        # Format large/small numbers with engineering notation if appropriate
        if isinstance(result, (float, np.float64)) and (abs(result) > 1e12 or (abs(result) < 1e-6 and abs(result) != 0)):
             return f"{result:.4e}"
        
        return str(result)
    except Exception:
        return "Syntax Error"

# --- State Management ---

if 'display' not in st.session_state:
    st.session_state.display = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = 0.0
if 'memory' not in st.session_state:
    st.session_state.memory = 0.0

# --- Button Handlers ---

def handle_button_press(key):
    """Updates the display and state based on the button pressed."""
    
    current_display = st.session_state.display
    
    if key == 'AC':
        st.session_state.display = ""
        st.session_state.last_result = 0.0
        st.session_state.memory = 0.0 # Clear memory too
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
        
    # --- Memory Operations ---
    elif key == 'M+':
        try:
            # Evaluate the current expression and add to memory
            value_to_add = float(safe_eval(current_display))
            st.session_state.memory += value_to_add
            st.session_state.display = f"M+ {value_to_add:.2f}" # Show what was added
        except Exception:
            st.session_state.display = "M+ Error"
    elif key == 'MR':
        # Recall Memory - insert memory value into display
        st.session_state.display += str(st.session_state.memory)
        
    # --- Basic Button Press ---
    else:
        # Append the key, handling functions that need an opening parenthesis
        if key in ('sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'exp', 'Abs', 'log_b'):
            st.session_state.display += f"{key}("
        else:
            st.session_state.display += key

# --- Streamlit UI ---

st.set_page_config(page_title="Ultimate Scientific Calculator", layout="centered")

# Inject custom CSS for styling
st.markdown(
    """
    <style>
    /* Main app background */
    .stApp {
        background-color: #F8C8DC; /* Baby Pink */
    }
    /* Buttons Styling */
    .stButton > button {
        background-color: white;
        color: black;
        border: 1px solid #ccc; /* Light grey border */
        font-weight: bold;
        font-size: 1.1em;
        border-radius: 5px;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #f0f0f0; /* Slightly darker white on hover */
        border-color: #999;
    }
    /* Primary buttons (e.g., AC, =, DEL) */
    .stButton > button[data-testid="stButton-primary"] {
        background-color: white; /* Keep white for primary too */
        color: #E91E63; /* Pink text for primary buttons */
        border: 1px solid #E91E63;
    }
    .stButton > button[data-testid="stButton-primary"]:hover {
        background-color: #FFF0F5; /* Lighter pink on hover for primary */
        border-color: #C2185B;
    }

    /* Text input for display */
    .stContainer {
        background-color: #fff; /* White display background */
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💖 Scientific Calculator")
st.caption(f"Memory (M): **{st.session_state.memory:.2f}** | Last Answer (Ans): **{st.session_state.last_result:.2f}**")
st.markdown("---")

# --- Display Screen ---
# The display remains an HTML-formatted area for better control
with st.container(border=True, height=100):
    st.markdown(
        f"""
        <div style="text-align: right; overflow-x: auto; font-size: 28px; font-weight: bold; height: 30px; color: #333;">
            {st.session_state.display if st.session_state.display else '0'}
        </div>
        """, 
        unsafe_allow_html=True
    )
st.markdown("---")


# --- Button Grid (6x5 layout for more buttons) ---
button_rows = [
    # Row 1: Advanced Functions
    ['Abs', 'log_b(', '!', 'M+', 'MR'],
    # Row 2: Trig Functions and Reciprocal
    ['sin', 'cos', 'tan', '1/x', 'DEL'],
    # Row 3: Log, Exp, Power, Root, Clear
    ['log', 'ln', 'exp', 'sqrt', 'AC'],
    # Row 4: Constants, Numbers, Operators
    ['pi', '7', '8', '9', '/'],
    # Row 5: Numbers and Operators
    ['e', '4', '5', '6', '*'],
    # Row 6: Numbers and Operators
    ['^', '1', '2', '3', '-'],
    # Row 7: Bottom Row (0, decimal, Ans, equals)
    ['(', '0', '.', 'Ans', '+'],
    # Row 8: Final operator and equals
    [')', '00', ' ', ' ', '='] 
]

unique_key_counter = 0

for row_index, row in enumerate(button_rows):
    cols = st.columns(len(row))
    for col_index, button_label in enumerate(row):
        
        # We are overriding Streamlit's default button colors with CSS,
        # but 'primary' type can still be used to apply specific text colors if needed.
        # For this design, all buttons will visually be white with black/pink text due to CSS.
        if button_label in ('AC', '=', 'DEL'):
            btn_type = "primary" # Use 'primary' to hint for a distinct style in CSS
        else:
            btn_type = "secondary" # Default for other buttons
            
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
