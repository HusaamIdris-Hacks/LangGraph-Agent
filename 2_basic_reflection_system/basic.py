from typing import List, Sequence, TypedDict, Annotated, Any
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, add_messages
import time
load_dotenv()

from chains import generation_chain, reflection_chain

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

graph = StateGraph(AgentState)

REFLECT = "reflect"
GENERATE = "generate"

def generate_node(state: AgentState) -> dict[str, Any]:
    time.sleep(4)
    response = generation_chain.invoke({
        "messages": state["messages"]
    })

    return {"messages": [response]}


def reflect_node(state: AgentState) -> dict[str, List[HumanMessage]]:
    time.sleep(4)
    response = reflection_chain.invoke({
        "messages": state["messages"]
    })

    return {"messages": [HumanMessage(content=response.content)]}

graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)

graph.set_entry_point(GENERATE)

def should_continue(state: AgentState) -> str:
    if len(state["messages"]) > 4:
        return END
    return REFLECT

graph.add_conditional_edges(GENERATE, should_continue, {END: END, REFLECT: REFLECT})

graph.add_edge(REFLECT, GENERATE)

app = graph.compile()

"""# Saves an image file
with open("graph.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())"""

initial_input = {"messages": [HumanMessage(content="Write a tweet about the importance of Cheesecake to the world")]}

for event in app.stream(initial_input):
    for node_name, state_update in event.items():
        print(f"\n--- Finished: {node_name} ---")
        msg = state_update["messages"][-1]
        
        if isinstance(msg.content, list) and len(msg.content) > 0 and isinstance(msg.content[0], dict) and "text" in msg.content[0]:
            print(msg.content[0]["text"])
        else:
            print(msg.content)
        print("-" * 40)
