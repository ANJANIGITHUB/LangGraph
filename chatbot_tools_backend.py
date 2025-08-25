from langgraph.graph import StateGraph,START,END
from langchain_openai.chat_models import ChatOpenAI
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
from langchain.tools import Tool
import sqlite3
import requests
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.utilities import OpenWeatherMapAPIWrapper
import os
from langchain_tavily import TavilySearch
from datetime import datetime
from langchain_community.document_loaders import WeatherDataLoader

#activate environment
#load_dotenv()

#llm call
# llm=ChatOpenAI()

#tool 1 duckduckgo
#search_tool= DuckDuckGoSearchRun(region="us-en")



search_tool = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)

@tool
def get_date_time() ->datetime:
    """ This function returns current date and time"""
    now=datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time=now.strftime("%H:%M:%S")

    return current_date ,current_time

#tool 2 duckduckgo
@tool
def calculater(input1 : float ,input2 : float ,operation : str) -> dict:
    """This is a calculator tool. This is used to perform operation such as add , subtract , 
       multiply and divide based on operation mentioned between input1 and input2
    """
    try:
        if operation =="add":
            result = input1 + input2
        elif operation =="subtract":
            result = input1 - input2
        elif operation =="multiply":
            result = input1 * input2
        elif operation =="divide":
            result = input1 / input2
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"input1": input1, "input2": input2, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}
    
#tool 3 ,search of stocks prices
@tool
def get_stock_price(symbol : str)->dict:
        """
          Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
          using Alpha Vantage with API key in the URL.
        """
        url=f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=8YKKJTTR02SRUN6K'
        r=requests.get(url)

        return r.json()

#tool 4 ,weather api
#os.environ["OPENWEATHERMAP_API_KEY"] = "d978e7e49ac217427988016bee132d4b"
weather= OpenWeatherMapAPIWrapper()

# 2. Wrap it as a Tool
weather_tool = Tool(
    name="Weather",
    func=weather.run,
    description="Get the current weather for a city of the given location"
)


#bind tools
tools_list=[search_tool,calculater,get_stock_price,weather_tool,get_date_time]
#llm_with_tools=llm.bind_tools(tools_list)

#create class ChatState
class ChatState(TypedDict):
    api_key:str
    messages:Annotated[list[BaseMessage],add_messages]

#Node
def ChatNode(state:ChatState):
    """Node that may answer the user query or request for a tool"""
    llm=ChatOpenAI(model='gpt-4o-mini',openai_api_key=state['api_key'])
    llm_with_tools=llm.bind_tools(tools_list)
    messages=state['messages']
    response=llm_with_tools.invoke(messages)
    return {'messages':[response]}

#tool node
tools=ToolNode(tools_list)

#checkpointer
conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)

#graph building
graph=StateGraph(ChatState)
graph.add_node("ChatNode",ChatNode)
graph.add_node("tools",tools)

graph.add_edge(START,"ChatNode")
graph.add_conditional_edges("ChatNode",tools_condition)
graph.add_edge("tools","ChatNode")

chatbot=graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    thread_latest_ts = {}
    for checkpoint in checkpointer.list(None):
        tid = str(checkpoint.config['configurable']['thread_id'])
        ts = getattr(checkpoint, "ts", None)  # or checkpoint["ts"] if dict
        if tid not in thread_latest_ts or (ts and ts > thread_latest_ts[tid]):
            thread_latest_ts[tid] = ts

    # Sort threads by timestamp (latest first)
    sorted_threads = sorted(thread_latest_ts.keys(), key=lambda t: thread_latest_ts[t] or 0, reverse=False)
    return sorted_threads


