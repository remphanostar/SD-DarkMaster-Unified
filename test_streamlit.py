import streamlit as st

st.title("🎨 SD-DarkMaster-Pro Test")
st.write("This is a simple test to check if Streamlit works properly.")

# Basic test elements
st.subheader("Test Elements")
st.success("✅ Streamlit is working!")
st.info("ℹ️ This is an info message")
st.warning("⚠️ This is a warning message")

# Interactive elements
name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}! 👋")

if st.button("Test Button"):
    st.balloons()
    st.write("🎉 Button clicked successfully!")

# Show some metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Test Metric 1", "42")
with col2:
    st.metric("Test Metric 2", "100%")
with col3:
    st.metric("Test Metric 3", "Working")