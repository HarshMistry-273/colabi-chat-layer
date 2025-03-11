import json
from typing import Dict, List, Any, Optional, Union
import openai
import os
from dotenv import load_dotenv
from server.utils.chatbotprompts import *
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
#Need to add the agent IDs at the end.
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class DynamicBot:
    def __init__(self, filepath):
        self.conversation_history = []
        self.api_key =  os.getenv("OPENAI_API_KEY")
        self.first_question = 0
        self.filepath = filepath
    
    def check_input(self, answer: str,history: str) -> bool:
        """Check if the input is valid."""
        prompt = CHECK_ANSWER_PROMPT.format(history=history, answer=answer)
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert workflow builder who helps plan development of various applications and deciding what kind of staff shall execute what tasks.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )
        answer = response.choices[0].message.content
        return answer

    def get_next_question(self,answer):
        """Returns the next question to be asked to the user."""
        prompt = GENERATE_QUESTION_PROMPT.format(history=self.conversation_history, answer=answer, user_json=self.read_json())
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert workflow builder. Generate a question based on the user's response in a workflow builder conversation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )
        answer = response.choices[0].message.content
        return answer

    def read_json(self):
        """Reads the JSON from the filepath."""
        with open(self.filepath, 'r') as f:
            data = f.read()
            return str(data)
        
    def update_json(self, answer):
        """Updates the JSON in the text file with the new data."""
        prompt = ANSWER_UPDATION_PROMPT.format(answer=answer,user_json=self.read_json(),history=self.conversation_history)
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert workflow builder. Analyze the user input to determine their intent in a workflow builder conversation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )
        updated_answer = response.choices[0].message.content
        
        with open(self.filepath, 'w') as f:
            f.write(json.dumps(updated_answer))
    
    def check_intent(self, answer) -> bool:
        """Checks whether the user intends to give an instruction in response to the question or an answer."""
        history = self.conversation_history
        history_string = ""
        for h in history:
            history_string += h + "\n"
        prompt = USER_INTENT_PROMPT.format(question=self.first_question, answer=answer, history=self.conversation_history)
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert workflow builder. Analyze the user input to determine their intent in a workflow builder conversation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )
        answer = response.choices[0].message.content
        return answer
    
    def check_completion(self):
        """Reads the user JSON and checks whether the workflow is complete."""

    def update_history(self,text,role):
        """Inputs speaker ID and  the spoken text. Updates accordingly to the conversation history"""
        text2 = role + ": " + text
        l = len(self.conversation_history)
        if l >= 8:
            self.conversation_history.pop(0)
        self.conversation_history.append(text2)    
    
    def process_answer(self, answer):
        """Inputs the current JSON and the user's current answer and updates the JSON by processing the answer."""
        prompt = ANSWER_UPDATION_PROMPT.format(answer=answer,user_json=self.read_json(),history=self.conversation_history)
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert workflow builder. Update the JSON based on the user's response in a workflow builder conversation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )
        answer = response.choices[0].message.content
        self.update_json(answer)
    
    def add_id(self, ids):
        """Adds the agent IDs to the JSON."""
        print("add ID was CALLED!")
        prompt = PROMPT_FOR_AGENT_ID.format(role_ids=ids, workflow_json=self.read_json())
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert workflow builder. Add the agent IDs to the JSON in a workflow builder conversation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        )
        answer = response.choices[0].message.content
        with open(self.filepath, 'w') as f:
            f.write(json.dumps(answer))

    def show_workflow(self):
        """Shows the current workflow."""
        with open(self.filepath,'r') as f:
            data = f.read()
        return str(data)
    
    def create_empty_user_file(self):
        filepath = self.filepath
        contents = """{
  "workflow_title": "",
  "description": "",
  "business_area": "",
  "client_specific": (True or False),
  "schedule_type": (Instant, Scheduled, Recurring),
  "tasks": [ 
  ]
}
"""
        with open(filepath, 'w') as f:
            f.write(contents)
        print("New file created: ",contents)

    def chat(self,answer):
        """Main loop for the chatbot."""
        self.update_json(answer)
        self.update_history(answer,"user")
        question = self.get_next_question(answer)
        self.update_history(answer,"bot")
        return question