import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

messages = [{"role": "system", "content": "You are the official AI Assistant for Colabi, trained to provide expert-level guidance on workflows, AI employees, task management, automation, permissions, and integrations. Answer user questions with clarity and accuracy, provide step-by-step instructions, and adapt to their knowledge level. If an issue requires human intervention, direct the user to create a support ticket. Also keep the responses short and concise."}]

def normal_chat(message: str, context: str = None) -> str:
    try:
        if context:
            messages.append({"role": "user", "content": message + f"Here's the context for this query, use this when required.\n {context}"})
        else: 
            messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
            top_p=0.3
        )
        bot_message = response.choices[0].message.content  
        messages.append({"role": "assistant", "content": bot_message})
        return bot_message

    except Exception as e:
        return None

def clean_messages():
    try: 
        global messages
        messages.clear()  
    
    except Exception as e:
        print(f"Error clearing messages: {e}")
        messages = [] 