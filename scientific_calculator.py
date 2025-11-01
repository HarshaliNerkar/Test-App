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
