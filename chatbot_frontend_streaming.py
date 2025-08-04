import streamlit as st
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage
from openai import AuthenticationError

st.title('Welcome to QnA Chatbot')

# Sidebar content
st.sidebar.title("User Details")
st.sidebar.markdown("**Build by:** Anjani Kumar")
st.sidebar.markdown("**Domain:** ML, Deep Learning , NLP & GenAI Expert ")
st.sidebar.markdown("**Location:** Bangalore, India")
st.sidebar.markdown("**Tech Stacks:** \n\n OpenAI GPT Models,LangGraph")

# Sidebar section
with st.sidebar:
    st.subheader("🔐 Configuration")
    user_api_key = st.text_input("Enter your OpenAI API Key", type="password")

st.sidebar.markdown(
    """
    <a href="https://www.linkedin.com/in/anjani-kumar-9b969a39/" target="_blank" style="color: #1f77b4; text-decoration: underline;">
        View Linked Profile
    </a>
    """,
    unsafe_allow_html=True
)


if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

thread_id='1'
CONFIG={'configurable':{'thread_id':thread_id}}

#load the message history

for message in  st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input=st.chat_input('Ask Any question')
# user_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    if user_api_key:
        try:
            response=chatbot.invoke({'api_key': user_api_key,'messages':[HumanMessage(content=user_input)]},config=CONFIG)
        except AuthenticationError:
            st.error("❌ Invalid API key. Please re-check it.\n\n"
                     "🔑 You can generate one here: [OpenAI API Keys](https://platform.openai.com/account/api-keys)")
            exit()
    else:
        st.write('API Key Field is Empty or Not Provided.Please Check')
        exit()
            
    #ai_message=response['messages'][-1].content

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'api_key': user_api_key,
                 'messages': [HumanMessage(content=user_input)]},
                config= {'configurable': {'thread_id': 'thread-1'}},
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

