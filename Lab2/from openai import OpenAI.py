from openai import OpenAI
from tavily import TavilyClient
import json
import os

# Simple .env loader
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
# Lab 2 of the agentic AI bootcamp
try:
    TAVILY_API = os.getenv("TAVILY_API_KEY")
    tavily = TavilyClient(api_key = TAVILY_API)
    print("API Client ready!")
    

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure you have the Tavily API key set in your environment variables.")


def calc_total(price, tax):
    total = price + (price * tax/100)
    return round(total, 2)
def web_search(query):
    response = tavily.search(query = query,
    include_answer = "advanced",
    search_depth = "advanced"
    )
    return response.get('answer', 'no answer found in the web')





client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= os.getenv("OPENROUTER_API_KEY"))
calc_schema = [
    {
        "type": "function",
        "function": {
            "name": "calc_total",
            "description": "calcualtes the total price of an item after tax",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number"},
                    "tax": {"type": "number"},
                },
                "required": ["price", "tax"],
            }
        }
    }
]

search_schema = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Performs a web search using Tavily. Returns the answer found in the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for on the web"
                    },
                },
                "required": ["query"],
            }
        }
    }
]



print ("Sending prompt to AI...")
def multi_tool_chat():
    tools_available = calc_schema + search_schema
    messages = [{"role": "user", "content": "You are a ReAct agent with access to a calculator and a web search tool.  Before using a tool, write your reasoning."}]

    print("Enter your prompt")
    while (True):
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        
        messages.append({"role": "user", "content": user_input})
    
        for step in range(4):
            response = client.chat.completions.create(
            model="qwen/qwen3.6-flash",
            messages=messages,
            tools=tools_available
            )
            ai_message = response.choices[0].message
            if ai_message.content and ai_message.tool_calls:
                print(f"thinking... {ai_message.content.strip()}")
            if not ai_message.tool_calls:
                print("\n message content: " + ai_message.content)
                messages.append(ai_message)
                break

            messages.append(ai_message)

            for tool_call in ai_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                print(f"\nCalling function: {function_name}")
                print(f"Arguments: {arguments}")

                if function_name == "calc_total":
                    result = calc_total(arguments["price"], arguments["tax"])
                elif function_name == "web_search":
                    result = web_search(arguments["query"])
                else:
                    result = "Unknown function"
            
                print(f"tool result: {result}")
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(result),
            })
        else: print("Too many steps...")
multi_tool_chat()
    
    

    
    
    
    
