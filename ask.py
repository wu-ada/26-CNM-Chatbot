import streamlit as st
st.write("Hello! I can assist you extra assistance. Please fill out the form below:")

# Form creation
with st.form(key="user_form"):
    # form fields
    first_name = st.text_input("First Name:")
    last_name = st.text_input("Last Name:")

    email = st.text_input("Email:")
  
    subject = st.text_input("Subject:")
    message = st.text_input("Message:")
    agree_terms = st.checkbox("I agree to the terms and conditions")

    # Submit button
    submit_button = st.form_submit_button(label="Submit")

    # When form is submitted
    if submit_button:
        if agree_terms:
            st.write(f"Thank you {first_name + ' ' + last_name}! We have received your request.")
        else:
            st.write("You must agree to the terms and conditions to submit the form.")
