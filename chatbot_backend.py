#Import Required libraries
from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

#activate the environment
#load_dotenv()

#Create the model
#model=ChatOpenAI(model='gpt-4o-mini')

#create a class
class ChatStateHolder(TypedDict):
    api_key:str
    messages:Annotated[list[BaseMessage],add_messages]


def chat_node(state:ChatStateHolder):
    model=ChatOpenAI(model='gpt-4o-mini',openai_api_key=state['api_key'])
    message=state['messages']
    chat_response=model.invoke(message)

    return {'messages':[chat_response]}


#Checkpointer
checkpointer=InMemorySaver()
#Add the graph

graph=StateGraph(ChatStateHolder)

#Add node
graph.add_node("chat_node",chat_node)

#Add edges
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

#Compile graph
chatbot=graph.compile(checkpointer=checkpointer)


# #Test by invoking
# thread_id='1'
# config={'configurable':{'thread_id':thread_id}}
# initial_state={'messages':[HumanMessage(content='What is the capital of india')]}
# result=chatbot.invoke(initial_state,config=config)

# print(result['messages'][-1].content)

