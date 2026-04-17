from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an elite Tech Twitter influencer tasked with writing highly engaging, viral tweets.\n"
            "Your goal is to generate the best possible tweet based on the user's request.\n\n"
            "RULES:\n"
            "- If the user provides a critique, you must respond with a revised version of your previous attempt that strictly follows their feedback.\n"
            "- CRITICAL: Output ONLY the raw text of the tweet itself.\n"
            "- DO NOT include any meta-commentary, explanations, strategy notes, or 'Here is your tweet:' introductions.\n"
            "- DO NOT acknowledge the critique; just output the new tweet."
        ),
        MessagesPlaceholder(variable_name="messages"),

    ]
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
            "Always provide detailed feedback and recommendations for the user's tweet, including requests for length, virality, style, etc.",   
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.9
)
generation_chain = generation_prompt | llm
reflection_chain = reflection_prompt | llm