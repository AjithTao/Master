#!/usr/bin/env python3
"""
Simple Streamlit test to isolate the issue
"""

import streamlit as st
from src.llm import chat

st.title("Simple LLM Test")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat([{"role": "user", "content": prompt}])
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
