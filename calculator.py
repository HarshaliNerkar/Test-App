import streamlit as st

# --- App Title ---
st.set_page_config(page_title="Simple Calculator", page_icon="🧮")
st.title("🧮 Simple Calculator")
st.write("A basic calculator built with Streamlit")

# --- Input Section ---
st.subheader("Enter Numbers:")
num1 = st.number_input("Enter first number", step=1.0, format="%.2f")
num2 = st.number_input("Enter second number", step=1.0, format="%.2f")

# --- Operation Selection ---
operation = st.selectbox(
    "Select Operation",
    ("Addition", "Subtraction", "Multiplication", "Division")
)

# --- Calculate Button ---
if st.button("Calculate"):
    if operation == "Addition":
        result = num1 + num2
        st.success(f"Result: {num1} + {num2} = {result}")

    elif operation == "Subtraction":
        result = num1 - num2
        st.success(f"Result: {num1} - {num2} = {result}")

    elif operation == "Multiplication":
        result = num1 * num2
        st.success(f"Result: {num1} × {num2} = {result}")

    elif operation == "Division":
        if num2 != 0:
            result = num1 / num2
            st.success(f"Result: {num1} ÷ {num2} = {result}")
        else:
            st.error("Error: Division by zero is not allowed.")

# --- Footer ---
st.caption("Built with ❤️ using Streamlit")
