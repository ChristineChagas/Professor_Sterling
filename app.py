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
import io
from io import StringIO
import openpyxl

# Set warnings to ignore
warnings.filterwarnings("ignore")

# Define the page config at the start
st.set_page_config(
    page_title="Professor Sterling: The Trading Expert",
    page_icon="Images/professor_sterling.png",
    layout="wide"
)

# Load external CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("CSS file not found. Ensure 'styles.css' is in the app directory.")

# Initialize session state for tracking page views and unique visitors
for key, default in [("page_views", 0), 
                     ("unique_visitors", set()), 
                     ("user_id", ''.join(random.choices(string.ascii_letters + string.digits, k=8)))]:
    st.session_state.setdefault(key, default)

# Increment page views
st.session_state.page_views += 1
st.session_state.unique_visitors.add(st.session_state.user_id)

# System prompt for Professor Sterling
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

# Initialize message state
if 'message' not in st.session_state:
    st.session_state['message'] = []
    st.session_state.message.append({"role": "system", "content": System_Prompt})
    st.session_state.message.append({"role": "assistant", "content": "Welcome! I'm Professor Sterling, your guide through the fascinating world of trading and finance. What would you like to learn about today?"})

# Sidebar setup
with st.sidebar:
    st.image("Images/professor_sterling.png", use_column_width=True)
    
    openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not openai.api_key:
        st.warning("Please set your OpenAI API key in the app's secrets.")
    else:
        st.success("API key detected. You're good to go!")
    
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

# Main page content
if selected_option == "AI Model":
    st.image("Images/ai_republic.png", width=100)
    st.markdown("""
        <div style="background-color: #121212; 
                    color: #F2F2F2; 
                    padding: 20px 25px; 
                    border-radius: 15px; 
                    border: 1px solid #2C2C2C;
                    margin-bottom: 20px;">
            <h2>James Sterling: The Trading Expert</h2>
            <p>Welcome! I’m Professor Sterling, here to guide you through the fascinating world of trading and finance.</p>
        </div>
    """, unsafe_allow_html=True)

elif selected_option == "Talk to Professor Sterling":
    st.image("Images/ai_republic.png", width=100)
    
    for messages in st.session_state.message:
        if messages['role'] != 'system':
            role_class = "assistant" if messages['role'] == "assistant" else "user"
            avatar = "Images/professor_sterling.png" if role_class == "assistant" else None
            with st.chat_message(role_class, avatar=avatar):
                st.markdown(messages["content"], unsafe_allow_html=True)

    if user_message := st.chat_input("Ask Professor Sterling"):
        st.session_state.message.append({"role": "user", "content": user_message})

        chat = openai.ChatCompletion.create(
            model="gpt-4",
            messages=st.session_state.message,
            temperature=0.5,
            max_tokens=1500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response = chat.choices[0].message.content
        st.session_state.message.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar="Images/professor_sterling.png"):
            st.markdown(response, unsafe_allow_html=True)

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
            <p>Upload your financial documents for professional analysis and insights.</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload a file", type=['pdf', 'docx', 'xlsx', 'csv'])
    
    if uploaded_file is not None:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size > 10:
            st.error("File size too large. Please upload a file smaller than 10MB.")
        else:
            try:
                file_extension = uploaded_file.name.split('.')[-1].lower()
                document_text = ""

                if file_extension == 'pdf':
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    document_text = ''.join(page.extract_text() for page in pdf_reader.pages)

                elif file_extension == 'docx':
                    doc = docx.Document(uploaded_file)
                    document_text = '\n'.join(para.text for para in doc.paragraphs)

                elif file_extension == 'xlsx':
                    df = pd.read_excel(uploaded_file)
                    document_text = df.to_string()

                elif file_extension == 'csv':
                    df = pd.read_csv(uploaded_file)
                    document_text = df.to_string()

                if document_text.strip():
                    prompt = f"""Analyze this document with the following content:\n{document_text[:4000]}"""
                    st.session_state.message.append({"role": "user", "content": prompt})
                    
                    chat = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=st.session_state.message,
                        temperature=0.5,
                        max_tokens=1500,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
                    response = chat.choices[0].message.content
                    st.markdown(response, unsafe_allow_html=True)
                else:
                    st.error("The document is empty or unreadable.")
            except Exception as e:
                st.error(f"Error processing file: {e}")

elif selected_option == "Sterling's Starling Awardee":
    st.image("Images/ai_republic.png", width=100)
    st.markdown("""
        <div style="background-color: #121212; 
                    color: #F2F2F2; 
                    padding: 20px 25px; 
                    border-radius: 15px; 
                    border: 1px solid #2C2C2C;">
            <h3>Christine Chagas 🌟</h3>
            <p>Remarkable student and the recipient of the Sterling’s Starling Award!</p>
        </div>
    """, unsafe_allow_html=True)
