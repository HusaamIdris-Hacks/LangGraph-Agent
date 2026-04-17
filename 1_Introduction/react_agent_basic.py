from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

# Gemini 2.5 Flash has a massive free quota (approx 500 requests/day)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.9
)

tools = [TavilySearchResults(max_results=3, depth="basic")]

agent = create_agent(
    model=llm,
    tools=tools,
)

# Invoke expects standard chat messages
response = agent.invoke({
    "messages": [{"role": "user", "content": "What is the capital of France?"}]
})

# Print the final response
print(response["messages"][-1].content)