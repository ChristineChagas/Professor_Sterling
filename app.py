# Add imports for Streamlit and other necessary packages at the beginning of your code if they aren’t there already

# Set the professor, AI model, and awardee image URLs
professor_image_url = "https://github.com/ChristineChagas/Professor_Sterling/blob/main/Images/professor_sterling.png?raw=true"
ai_republic_image_url = "https://github.com/ChristineChagas/Professor_Sterling/blob/main/Images/ai_republic.png?raw=true"
christine_image_url = "https://github.com/ChristineChagas/Professor_Sterling/blob/main/Images/christine.jpg?raw=true"

# Main page content based on the selected option
if selected_option == "Talk to Professor Sterling":
    st.image(ai_republic_image_url, width=100)
    
    # Display existing messages in chat
    for messages in st.session_state.message:
        if messages['role'] == 'system':
            continue
        
        if messages['role'] == "assistant":
            with st.chat_message("assistant", avatar=professor_image_url):
                st.markdown(messages["content"])
        else:
            st.chat_message("user").markdown(messages["content"])

    # Handle new user input
    if user_message := st.chat_input("Say something"):
        st.session_state.message.append({"role": "user", "content": user_message})

        # Process response based on user input
        if any(phrase in user_message.lower() for phrase in [
            "favorite student", "favourite student", "fave student", 
            "best student", "top student", "star student",
            "favorite pupil", "favourite pupil", "fave pupil",
            "favorite mentee", "favourite mentee", "fave mentee"
        ]):
            assistant_response = "Without a doubt, my favorite student is Christine Chagas. Her dedication and improvement in class are unparalleled."
        else:
            try:
                completion = openai.ChatCompletion.create(model="gpt-4", messages=st.session_state.message)
                assistant_response = completion.choices[0].message['content']
            except:
                assistant_response = "Professor Sterling is away on a call—try again in a moment."

        st.session_state.message.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant", avatar=professor_image_url):
            st.markdown(assistant_response)

elif selected_option == "Sterling's Starling Awardee":
    st.image(ai_republic_image_url, width=100)
    
    # Display Sterling's Starling Award section
    st.markdown("""
        <h2 style='color: #F2F2F2;'>Sterling's Starling Award</h2>
        <p style='color: #D2D2D2;'>The recipient of Sterling's Starling Award is given to the most improved in class.</p>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns(2)
    with left_col:
        st.image(christine_image_url)
    with right_col:
        st.markdown("""
            <p style='color: #F2F2F2;'>
                Christine Chagas<br><span style='color: #B3B3B3;'>Star Student</span> ⭐
            </p>
        """, unsafe_allow_html=True)
