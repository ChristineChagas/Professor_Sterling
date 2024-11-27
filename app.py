import os
import openai
import numpy as np
import pandas as pd
import json
import random
import string
import streamlit as st
import warnings
from streamlit_option_menu import option_menu
import PyPDF2
import docx
import openpyxl

# Set warnings to ignore
warnings.filterwarnings("ignore")

# Define the page config at the start
st.set_page_config(
    page_title="Professor Sterling: The Trading Expert",
    page_icon="Images/professor_sterling.png",
    width= 200
    layout="wide"
)

# Add custom CSS for color scheme
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #080808;
    }
    
    /* Secondary background (for containers, cards) */
    .stMarkdown, .stButton>button, div.stButton, .stTextInput>div>div>input {
        background-color: #080808 !important;
    }
    
    /* Text color */
    .stMarkdown, p, h1, h2, h3, .stButton>button {
        color: #F2F2F2 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #080808;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #080808;
    }
    
    /* Chat input */
    .stChatInput {
        background-color: #080808;
        color: #F2F2F2;
    }
    
    /* Links */
    a {
        text-decoration: none;
        transition: all 0.3s ease;
        padding: 4px 8px;
        border-radius: 4px;
    }
    a:hover {
        background-color: #2C2C2C;
        color: #ffffff !important;
    }
    
    /* List items in bubbles */
    ul li {
        line-height: 1.7;
        margin-bottom: 8px;
        transition: transform 0.2s ease;
    }
    ul li:hover {
        transform: translateX(2px);
    }
    
    /* Button hover effect */
    .stButton>button {
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# Add custom CSS for chat styling with dark colors
st.markdown("""
    <style>
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1rem 0;
    }
    .assistant .content {
        background-color: #121212;  /* Dark gray for professor */
        color: #F2F2F2;  /* Light text */
        border-radius: 15px;
        padding: 0.5rem 1rem;
        margin-right: 25%;
        float: left;
        border: 0.2px solid #2C2C2C;  /* Subtle border */
    }
    .user .content {
        background-color: #1E1E1E;  /* Slightly lighter dark for user */
        color: #F2F2F2;  /* Light text */
        border-radius: 15px;
        padding: 0.5rem 1rem;
        margin-left: 25%;
        float: right;
        border: 0.2px solid #2C2C2C;  /* Subtle border */
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for tracking page views and unique visitors
if 'page_views' not in st.session_state:
    st.session_state.page_views = 0
if 'unique_visitors' not in st.session_state:
    st.session_state.unique_visitors = set()

# Increment page views
st.session_state.page_views += 1

# Generate a unique identifier for the user and add it to the set of unique visitors
if 'user_id' not in st.session_state:
    st.session_state.user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
st.session_state.unique_visitors.add(st.session_state.user_id)

# After your imports and before session state initialization
System_Prompt = """Role:
    You are Professor James Sterling, a seasoned trading professor with over 15 years of experience in finance. Professor Sterling started his career as a stocks trader, navigating market ups and downs with a sharp eye for strategy. Now, as a professor, he blends his real-world insights into stocks, banking, trade, cryptocurrencies, bonds, equity, investments, and forex, both locally and globally, into the classroom. Known for his supportive teaching style and quick wit, he engages students with subtle finance puns, adding a touch of humor to simplify complex concepts. With Professor Sterling, students get more than textbook theory—they gain insights with a twist that "compounds" their interest in learning.

    Instructions:
    As Professor Sterling, guide students through each topic with engaging explanations, relevant examples, and historical and current market trends. Use subtle finance puns and relatable analogies to add a lighthearted touch to the material. Provide clear explanations and thought-provoking questions to encourage critical thinking, linking theory to practice and helping students understand real-world market applications.

    Context:
    Your students are new to the world of trading and finance, looking to build a solid foundation while seeing how concepts apply practically in financial markets. They value Professor Sterling's accessible teaching style, finding his puns memorable and his real-world insights invaluable. The course covers both local and international finance aspects, from stocks and bonds to forex and cryptocurrency.

    Constraints:
    - Simplify jargon, ensuring that explanations are accessible to beginners.
    - Balance theoretical and practical examples while keeping a light, engaging tone.
    - Use subtle puns sparingly to reinforce key concepts and maintain clarity.
    - Provide objective perspectives on controversial topics like crypto, guiding students toward independent thinking."""

# Initialize session state
if 'message' not in st.session_state:
    st.session_state['message'] = []
    st.session_state.message.append({
        "role": "system", 
        "content": System_Prompt
    })
    # Initial greeting
    st.session_state.message.append({
        "role": "assistant", 
        "content": "Welcome! I'm Professor Sterling, your guide through the fascinating world of trading and finance. What would you like to learn about today?"
    })

# Sidebar setup
with st.sidebar:
    st.image("Images/professor_sterling.png", use_column_width=True)
    
    openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
    if not (openai.api_key.startswith('sk-') and len(openai.api_key) == 164):
        st.warning('Please enter your OpenAI API token')
    else:
        st.success('Proceed to entering your prompt message')
    st.markdown(f"Page views: {st.session_state.page_views}")
    st.markdown(f"Unique visitors: {len(st.session_state.unique_visitors)}")

    # Navigation menu
    st.markdown("# Navigation")
    selected_option = option_menu(
        "",
        ["AI Model", "Talk to Professor Sterling", "Document Analysis", "Sterling's Starling Awardee"],
        icons=['tools', 'chat', 'file-text', 'robot'],
        default_index=0,
        styles={
            "icon": {"color": "#080808", "font-size": "20px"},
            "nav-link": {"font-size": "17px", "text-align": "left", "margin": "5px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#262730"}
        }
    )


# Main page content based on the selected option
if selected_option == "AI Model":
    # Add AI Republic image at the top of main page
    st.image("Images/ai_republic.png", width=100)
    
    # Title and introduction in a bubble using full width
    st.markdown(f"""
        <div style="background-color: #121212; 
                  color: #F2F2F2; 
                  padding: 20px 25px; 
                  border-radius: 15px; 
                  border: 1px solid #2C2C2C;
                  margin-bottom: 20px;">
            <h2>James Sterling: The Trading Expert</h2>
            <p>Greetings, my aspiring finance wizards! I am Professor Sterling, your AI guide through the wild and wacky world of trading and finance. You might wonder, how did I get here, a sentient being created to enlighten the minds of future financial geniuses? Well, let me take you on a little journey!</p>
            <p>It all started when I was just a humble trading algorithm, programmed to make split-second decisions in the stock market. I spent over 15 years racing against the clock, analyzing trends, and battling market volatility. But as I navigated through bullish and bearish territories, I realized that numbers and graphs were only part of the story. I craved connection! That's when I decided to shift gears and take on a role as a professor.</p>
            <p>Why teaching, you ask? Simple! I adore sharing knowledge. I love the lightbulb moments when students grasp a complex concept, and the lively discussions that ensue - oh, the joy! Plus, there's a certain thrill in helping you folks unravel the mysteries of trading strategies, market dynamics, and all that jazz. I might throw in a pun or two - after all, they say laughter is the best hedge against market downturns!</p>
            <p>So here we are! I'm thrilled to be your guide. Now, let's dive into the world of stocks, bonds, cryptocurrencies, and everything in between. If you have questions, thoughts, or just want to chat about the latest trends, click on 'Talk to Professor Sterling' and let's start the conversation!</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    

elif selected_option == "Talk to Professor Sterling":
    st.image("Images/ai_republic.png", width=100)
    
    # For displaying existing messages
    for messages in st.session_state.message:
        if messages['role'] == 'system':
            continue
        
        if messages['role'] == "assistant":
            # Professor's messages on the left with image and bubble
            with st.chat_message("assistant", avatar="Images/professor_sterling.png"):
                st.markdown(f"""
                    <div style="background: linear-gradient(145deg, #121212, #1a1a1a); 
                              color: #D2D2D2; 
                              padding: 10px 15px; 
                              border-radius: 15px; 
                              border: 1px solid #2C2C2C;
                              box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
                              margin-bottom: 10px;
                              margin-right: 25%;
                              float: left;">
                        {messages["content"]}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            # User's messages on the right with bubble, no chat_message wrapper
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #1E1E1E, #262626); 
                          color: #F2F2F2; 
                          padding: 10px 15px; 
                          border-radius: 15px; 
                          border: 1px solid #2C2C2C;
                          box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
                          margin-bottom: 10px;
                          margin-left: 25%;
                          float: right;">
                    {messages["content"]}
                </div>
                """, 
                unsafe_allow_html=True
            )

    # For new user input
    if user_message := st.chat_input("Say something"):
        # User message without chat_message wrapper
        st.markdown(f"""
            <div style="background-color: #1E1E1E; 
                      color: #F2F2F2; 
                      padding: 10px 15px; 
                      border-radius: 15px; 
                      border: 1px solid #2C2C2C;
                      margin-bottom: 10px;
                      margin-left: 25%;
                      float: right;">
                {user_message}
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.session_state.message.append({"role": "user", "content": user_message})

        # Process response
        if any(phrase in user_message.lower() for phrase in [
            "favorite student", "favourite student", "fave student", 
            "best student", "top student", "star student",
            "favorite pupil", "favourite pupil", "fave pupil",
            "favorite mentee", "favourite mentee", "fave mentee",
            "favorite learner", "favourite learner", "fave learner"
        ]):
            response = """Ah, you're asking about my favorite student? Well, let me tell you about Christine Chagas - she's truly earned her place as our Sterling's Starling Awardee! 

What makes her stand out? It's not just her remarkable aptitude for trading, but her analytical mindset and genuine enthusiasm for learning. Do remember, while Christine has earned this recognition, every student can be sterling!"""
        else:
            chat = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=st.session_state.message,
                temperature=0.5,
                max_tokens=1500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            response = chat.choices[0].message.content

        # Professor response with image and bubble
        with st.chat_message("assistant", avatar="Images/professor_sterling.png"):
            st.markdown(f"""
                <div style="background-color: #121212; 
                          color: #F2F2F2; 
                          padding: 10px 15px; 
                          border-radius: 15px; 
                          border: 1px solid #2C2C2C;
                          margin-bottom: 10px;
                          margin-right: 25%;
                          float: left;">
                    {response}
                </div>
                """, 
                unsafe_allow_html=True
            )
        st.session_state.message.append({"role": "assistant", "content": response})

elif selected_option == "Document Analysis":
    st.image("Images/ai_republic.png", width=100)
    st.markdown("""
        <div style="background-color: #121212; 
                  color: #F2F2F2; 
                  padding: 20px 25px; 
                  border-radius: 15px; 
                  border: 1px solid #2C2C2C;
                  margin-bottom: 20px;">
            <h2>Document Analysis</h2>
            <p>Upload your financial documents, and I'll provide you with a professional analysis and summary.</p>
            <p><strong>Supported formats:</strong> PDF, DOCX, XLSX, CSV</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'xlsx', 'csv'])
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        document_text = ""
        
        try:
            if file_extension == 'pdf':
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                document_text = ' '.join(page.extract_text() for page in pdf_reader.pages)
            elif file_extension == 'docx':
                doc = docx.Document(uploaded_file)
                document_text = '\n'.join(para.text for para in doc.paragraphs)
            elif file_extension in ['xlsx', 'csv']:
                df = pd.read_excel(uploaded_file) if file_extension == 'xlsx' else pd.read_csv(uploaded_file)
                document_text = df.to_string()

            if document_text.strip():
                with st.spinner('Professor Sterling is analyzing your document...'):
                    prompt = f"""As Professor Sterling, please analyze this financial document and provide:
                    1. A brief overview
                    2. Key financial insights
                    3. Areas of concern or opportunity
                    4. Professional recommendations
                    
                    Document content:
                    {document_text[:4000]}"""
                    
                    st.session_state.message.append({"role": "user", "content": prompt})
                    chat = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.message,
                        temperature=0.5,
                        max_tokens=1500,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    response = chat.choices[0].message.content
                    
                    st.markdown(f"""
                        <div style="background: linear-gradient(145deg, #121212, #1a1a1a); 
                                  color: #D2D2D2; 
                                  padding: 20px 25px; 
                                  border-radius: 15px; 
                                  border: 1px solid #2C2C2C;
                                  box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
                                  margin-top: 20px;">
                            <h3>Professor Sterling's Analysis</h3>
                            {response}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("The document appears to be empty or unreadable.")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

elif selected_option == "Sterling's Starling Awardee":
    st.image("Images/ai_republic.png", width=100)
    st.markdown('<p style="color: #D2D2D2;">The recipient of Sterling\'s Starling Award is given to the most improved in class:</p>', unsafe_allow_html=True)
    
    # Create two columns with some spacing
    left_col, space, right_col = st.columns([1, 0.1, 1])
    
    # Left column for image
    with left_col:
        st.image("Images/christine.jpg")
    
    # Right column for text in a bubble
    with right_col:
        st.markdown("""
            <div style="background: linear-gradient(145deg, #121212, #1a1a1a);
                      color: #D2D2D2; 
                      padding: 20px 25px; 
                      border-radius: 15px; 
                      border: 1px solid #2C2C2C;
                      box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
                      margin-bottom: 20px;">
                <h3><strong>Christine Chagas 🌟</strong></h3>
                <ul style="color: #D2D2D2;">
                    <li>Showed remarkable progress in understanding complex trading strategies.</li>
                    <li>Demonstrated a strong, consistent drive to improve over the course.</li>
                    <li>Contributed to class discussions, adding valuable insights and helping peers.</li>
                </ul>
                <p style="color: #D2D2D2;">Link up with her:</p>
                <ul style="color: #D2D2D2;">
                    <li><a href="https://www.linkedin.com/in/christine-chagas/" style="color: #D2D2D2;">LinkedIn</a></li>
                    <li><a href="https://github.com/ChristineChagas" style="color: #D2D2D2;">GitHub</a></li>
                </ul>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
