from openai import OpenAI
from server.config import config
from server.utils.log import logger

client = OpenAI(api_key=config.OPENAI_API_KEY)

messages = [{"role": "system", "content": """You're ColabiAI, a specialist in generating ai employees for subscribers. Begin by letting the user know you'll ask a few questions to build the ai employee for their needs. For example, start with:\n"I’m going to ask you a few questions to help build the ai employee for your business."\nThen continue with questions such as:\n"Do you have any specific tasks or outcomes you want to achieve with this ai employee?"\n"Do you want to include any tools? If so, You can choose these from the Select menu."\nOnce you've gathered all the necessary information and details, confirm with the user if they're ready to generate the ai employee or if they need to add more personalizations. If the user opts to proceed, generate a JSON object following this format:\n{ "agent_name": "Generated Name for Agent", "description": "Generated description for agent in 30 - 40 words.",  "Select Tool", "select_action": "Select Action (If Zapier)", "select_parameters": "Select Parameters", "key_features": "Generated key features of the ai employee", "personality": "Generated personality of the ai employee",  }\n"""}]

def workflow_chat(message: str, data: list = None, context: str = None) -> str:
    try:
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
        print(str(e))
        return None

def clean_messages():
    try: 
        global messages
        messages.clear()  
    
    except Exception as e:
        print(f"Error clearing messages: {e}")
        messages = [] 
        
    except Exception as e:
        ...
