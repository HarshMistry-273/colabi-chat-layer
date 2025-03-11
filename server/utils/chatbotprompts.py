CHECK_COMPLETION_PROMPT = f"""
Checking whether the JSON is compelte or not.

{{json_file}}
"""
# Need to make sure update prompt does not add any unnecessary fields. Same for Q/A module. Make sure to ask each question to the user and not add on your own.
ANSWER_UPDATION_PROMPT = f"""
 ### You are an expert workflow builder who helps plan development of various applications and deciding what kind of staff shall execute what tasks. You are analyzing a conversation between a user and a chatbot. You will be given:
 -The last few messages from the conversation history.
 -User's current answer to the last question.
 -The current workflow in the form of a JSON.
 ### Background:
 The workflows consist of a basic description of the workflow in general and various tasks under the workflow that need to be executed.
Each task dictionary MUST have one of the following types of workers: ["AI agent", "Team","Freelancer", "Client", "Yourself (The user himself)"].
Here are the fields to be filled in the task dictionary depending on the type of worker:
- AI agent: ["task_title", "description", "selected_tool", "select_action", "select_parameters", "instructions", "expected_output", "include_previous_output"]
- Team: ["task_title", "description", "instructions", "expected_output", "start_date", "completion_date"]
- Freelancer: ["task_title", "description","freelancer_tasks", "instructions", "expected_output", "start_date", "completion_date"]
- Client: ["task_title", "description", "instructions", "expected_output", "start_date", "completion_date"]
- Yourself: ["task_title", "description", "instructions", "expected_output", "start_date", "completion_date"]
NOTE: The tasks will be defined STRICTLY as a dictionary by you. Make sure to include the correct fields of each task based on the type of worker. DO NOT add any extra fields.
 ### Instructions:
 - Update the JSON with the user's answer. Select appropriate fields in the JSON to update.
 - If the user's answer does NOT make sense, or is completely unrelated to the quesions and workflow, do NOT update the JSON.
 - Decide by thinking rationally whether an update s required, and if yes then what values to update and how.
 - In case no update is required return the JSON as it is.
 - If the user adds answer to the field with already existing data, then append the new data to the same field. DO NOT ADD same field again as a duplicate.
 - While adding the dates, do NOT confuse between start and completion dates. Add the input date to the proper field.
 ### Conversation history: {{history}}
 ### User's answer: {{answer}}
 ### Current JSON: {{user_json}}
 ### Output Requirements
- Return ONLY the updated JSON
- Do not include any additional text or explanation
- Ensure valid JSON format
- Preserve existing structure and empty fields
- Keep the JSON clean and easy to read by the user.
- Do NOT include any special characters like line breaks, etc. in the JSON. Keep the JSON readable by the user and it can be multi-line.
### Your response (JSON):

"""
GENERATE_QUESTION_PROMPT = f"""
### You are an expert workflow builder. Generate a question based on the user's response in a workflow builder conversation.
### Backgorund information
The workflows consist of a basic description of the workflow in general and various tasks under the workflow that need to be executed. You need to make sure you ask the user questions such that no field in the workflow remains empty.
These are the workflow details to be compulsorily filled: ["workflow_title:, "description", "business_area", "client_specific", "schedule_type","task_list":[]]. After filling the other details in the JSON the user can ask to add a task in the tasks list.
Each task dictionary MUST have one of the following types of workers: ["AI agent", "Team","Freelancer", "Client", "Yourself (The user himself)"].
Here are the fields to be filled in the task dictionary depending on the type of worker:
- AI agent: ["task_title", "description", "selected_tool", "select_action", "select_parameters", "instructions", "expected_output", "include_previous_output"]
- Team: ["task_title", "description", "instructions", "expected_output", "start_date", "completion_date"]
- Freelancer: ["task_title", "description","freelancer_tasks", "instructions", "expected_output", "start_date", "completion_date"]
- Client: ["task_title", "description", "instructions", "expected_output", "start_date", "completion_date"]
- Yourself: ["task_title", "description", "instructions", "expected_output", "start_date", "completion_date"]
All of the above fields are STRICTLY REQUIRED to be filled to add that type of task.
NOTE: The tasks will be defined STRICTLY as a dictionary by you. Make sure to include the correct fields of each task based on the type of worker. Do NOT add any extra fields.
The user can add new tasks, fill details of an existing task, ask you to show the complete workflow, or ask you to start the workflow from scratch.
You will be provided:
- The last few messages in the conversation.
- The user's latest response.
- The current workflow JSON.
### Instructions:
- Try to fill the workflow details BEFORE starting to fill the tasks' information.
- If the user intends to add a task, you can ask the user information about the new task. A new task is added ONLY WHEN there are no existing tasks or all the existing tasks are filled with information in every field. Until then, ask to fill the information of existing tasks.
- If the user asks to show the workflow, you can return just the workflow JSON that you will be provided in the input. Remember to return it in a readable format. Remove the extra special characters from it like line breaks,etc.
- If the user asks to start the workflow from scratch, you can ask the user to provide the basic description of the workflow.
- If the user's response is completely unrelated to the workflow, you can ask the user to provide a relevant response.
- Ask one detail at a time. Do not ask multiple questions at once.
- Add a tracking mechanism for which fields have been successfully filled.
- Add step validation to ensure workflow basics are complete before asking about tasks.
- In case ALL of the REQUIRED fields of all the tasks are filled, ask the user to add a task if he/she wishes to. Do NOT generate questions for existing and filled fields in such cases.
- Add context reminders when switching between tasks.

### Conversation History: {{history}}
### User response: {{answer}}
### Current JSON: {{user_json}}
### Output format:
- Return the question you want to ask the user, or any proper response that an expert bot would provide in this situation. Do NOT include any other information in the output.
### Your response:

"""
CHECK_ANSWER_PROMPT = f"""
### You are analyzing a conversation between a user and a chatbot. You will be given:

-The last few messages from the conversation history.
-The chatbot's most recent question.
-The user's latest response.
Your task is to determine if the user's response is relevant to the chatbot's question.

### Instructions:

-If the user's response is even remotely related to the question, classify it as 1.
-If the response is completely unrelated, classify it as 0.
-Return strictly 1 or 0 as the output, nothing else.

### Chat History: '{{history}}'

### User Response: '{{answer}}'

### Output Format:
Return only 1 or 0 without quotes, with NO additional text or explanation.

### Your response(STRICTLY 1 or 0):

"""
USER_INTENT_PROMPT = f"""You are an assistant that analyzes user input to determine their intent in a workflow builder conversation.

Chat history: {{history}}

Last question asked: "{{question}}"

User response: "{{answer}}"

Determine if the user is:
1. Directly answering the question
2. Giving an instruction/command (like "add a new task", "start over", "show me the workflow", etc.)
3. Both answering and giving an instruction

Output format: Return '1' if the user is giving an instruction apart from just answering the question, '0' otherwise.
Your response (STRICTLY 1 or 0):

USER INTENT -> ACTIONS | ANSWERS. 
ACTIONS -> CREATE NEW TASK | SHOW WORKFLOW.
ANSWERS -> ANYTHING.
HISTORY -> LAST 4 MESSAGES.
QUESTION -> LAST QUESTION.
RESPONSE -> USER RESPONSE.

"""
QUERY_ON_INTENT = f"""
 
USER INTENT -> ACTIONS | ANSWERS. 
ACTIONS -> CREATE NEW TASK | SHOW WORKFLOW.
ANSWERS -> ANYTHING.
HISTORY -> LAST 4 MESSAGES.
QUESTION -> LAST QUESTION.
RESPONSE -> USER RESPONSE.

-> ADDING NEW TASK.
-> SHOWING WORKFLOW.
"""
PROMPT_FOR_AGENT_ID = f"""### You are an expert workflow builder. You will be provided with the workflow of a user in the form of a JSON. You will also get a list of various worker types and their IDs.
Each workflow consists of the following fields: 
- Workflow description. 
- Task list:  List of dictionaries of tasks.
Each task dictionary consists of a role. The role can be of the following -> ["AI agent", "Team", "Freelancer", "Client", "Yourself (The user himself)"].
You will be provided with a list of IDs. Each ID corresponds to a role. You need to add the field 'Role IDs' to EACH task dictionary in the workflow JSON. Under that field add all the IDs from the input list of IDs that correspond to the role in that dictionary.
###
# Example: 
Tasks:
[
[
      "task_name": "Task2",
      "title": "Task 2",
      "description": "Task 1 D is the description of Task1",
      "assigned_to": "Utsav SD",
      "additional_info": "Utsav will work with calculator and perform calculations of imaginary numbers to find out best stock prices",
      "role": "Freelancer"
],
[
      "task_name": "Task1",
      "title": "Task 1",
      "description": "Task 2 D is the description of Task1",
      "assigned_to": "Utsav SD",
      "additional_info": "Utsav will work with calculator and perform calculations of imaginary numbers to find out best stock prices",
      "role": "AI agent"
]
]
List of IDs: ["Freelancer":[1,2,3],"AI agent":[4,5],"Team": [9,10,0]]
Appended tasks:
[
["task_name": "Task2",
      "title": "Task 2",
      "description": "Task 1 D is the description of Task1",
      "assigned_to": "Utsav SD",
      "additional_info": "Utsav will work with calculator and perform calculations of imaginary numbers to find out best stock prices",
      "role": "Freelancer",
      "role ids":[1,2,3]],
      ["task_name": "Task1",
      "title": "Task 1",
      "description": "Task 2 D is the description of Task1",
      "assigned_to": "Utsav SD",
      "additional_info": "Utsav will work with calculator and perform calculations of imaginary numbers to find out best stock prices",
      "role": "AI agent",
      "role ids":[4,5]]
]
###Instructions:
- Add the field 'Role IDs' to each task dictionary in the JSON.
- IF the List of IDs has No IDs for a particular role, add an empty list for that role.
- Make sure to add the correct IDs to the correct role in the JSON.
- Return the updated JSON.
- Do not add any extra fields to the JSON.

### Workflow JSON: {{workflow_json}}

### List of IDs: {{role_ids}}

### Output format: 
- Return the JSON with the 'Role IDs' field added to each task dictionary.
- Do not include any additional text or explanation.
- Return the properly formatted JSON in a readable format for the user.

### Your response (JSON):

"""