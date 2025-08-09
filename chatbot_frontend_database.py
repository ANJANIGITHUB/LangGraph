import streamlit as st
from chatbot_database_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage
from openai import AuthenticationError
import uuid

st.title('Welcome to QnA Chatbot')

#***************************Utility Function*********************************************
def return_threadnums():
    uuidnum=uuid.uuid4()
    return uuidnum

def add_threads(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def reset_chat():
    st.session_state['thread_id']=return_threadnums()
    add_threads(st.session_state['thread_id'])
    st.session_state['message_history']=[]

# def load_messages(thread_id):
#     return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']

# def load_messages(thread_id):
#     return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

#****************************************************************************************

# Custom CSS for smaller font size
st.markdown("""
    <style>
    .small-font {
        font-size: px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar content
st.sidebar.title("👤 Profile")
st.sidebar.markdown(
    """
    <a href="https://www.linkedin.com/in/anjani-kumar-9b969a39/" target="_blank" style="color: #1f77b4; text-decoration: underline; font-size: 15px">
        LinkedIn
    </a>
    """,
    unsafe_allow_html=True
)
st.markdown(" ")
# st.sidebar.markdown("**Build by:** Anjani Kumar")
# st.sidebar.markdown("**Domain:** ML, Deep Learning , NLP & GenAI Expert ")
# st.sidebar.markdown("**Location:** Bangalore, India")
# st.sidebar.markdown("**Tech Stacks:** \n\n OpenAI GPT Models,LangGraph")
st.sidebar.markdown("""
<span style='color:#5D8AA8'><strong>Built by:</strong> Anjani Kumar</span>  \n
<span style='color:#A3C1AD'><strong>Domain:</strong> ML, DL, NLP, GenAI</span>  \n
<span style='color:#F4A7B9'><strong>Location:</strong> Bangalore, India</span>  \n
<span style='color:#FFD580'><strong>Stack:</strong> OpenAI GPT, LangGraph</span>
""", unsafe_allow_html=True)

# Sidebar section
with st.sidebar:
    st.subheader("🔐 Configuration")
    user_api_key = st.text_input("Enter your OpenAI API Key", type="password")


if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=return_threadnums()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread']=retrieve_all_threads()

if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.subheader('My Past Conversations')

# for thread_id in st.session_state['chat_thread'][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state['thread_id'] = thread_id
#         messages = load_conversation(thread_id)

#         temp_messages = []

#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 role='user'
#             else:
#                 role='assistant'
#             temp_messages.append({'role': role, 'content': msg.content})

#         st.session_state['message_history'] = temp_messages

# Add CSS for thread buttons
st.markdown("""
    <style>
    .thread-btn {
        display: block;
        width: 50%;
        padding: 4px 8px; /* Smaller padding */
        font-size: 10px;  /* Smaller font */
        background-color: #e6f0ff; /* Light blue default */
        border: 1px solid #99c2ff; /* Border color */
        border-radius: 3px;
        color: black;
        text-align: left;
        margin-bottom: 4px;
        cursor: pointer;
    }
    .thread-btn:hover {
        background-color: #cce0ff; /* Hover blue */
    }
    .thread-btn-active {
        background-color: #99c2ff; /* Active thread color */
        border: 1px solid #3366cc;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar loop
for thread_id in st.session_state['chat_thread'][::-1]:
    messages = load_conversation(thread_id)
    first_user_message = next(
        (msg.content for msg in messages if isinstance(msg, HumanMessage)),
        "No conversation yet"
    )

    preview_text = first_user_message.strip()
    if len(preview_text) > 20:
        preview_text = preview_text[:20] + "..."

    # Determine CSS class based on selection
    css_class = "thread-btn-active" if thread_id == st.session_state['thread_id'] else "thread-btn"

    # Use markdown for styled HTML button
    if st.sidebar.button(preview_text, key=f"thread_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        temp_messages = [
            {'role': 'user' if isinstance(msg, HumanMessage) else 'assistant', 'content': msg.content}
            for msg in messages
        ]
        st.session_state['message_history'] = temp_messages




#thread_id='1'
CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}}

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
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

