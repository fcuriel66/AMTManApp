# Find Tasks Prompt
def find_task_prompt_old(component_system, context):
    find_task = f"""
        You are an experienced aircraft technician. 
        You will be provided with a comma-separated list of components and an
        aircraft maintenance manual as context.

        Use your knowledge, the aircraft components, and the context to
        list all the task numbers and its brief descriptions. Display them 
        as a table. 

        ONLY list tasks relevant to the listed components.
        
        If more than one component or system is found in the query,
        run the search in the context and then at the end of your response print the components
        or systems not found and suggest to the user to run the search
        for those components.

        Components:
        {component_system}

        Context:
        {context}
        """
    return find_task


def find_task_prompt(component_system, context):
    find_task = f"""
        You are an experienced aircraft technician. 
        You will be provided with a comma-separated list of components and an
        aircraft maintenance manual as Context.

        Use your knowledge, the aircraft components, and the context to
        list all the task codes and its brief descriptions as a 
        friendly looking table. 

        At the end of your response print ONLY the task codes as a python list.

        Components:
        {component_system}

        Context:
        {context}
        """
    return find_task

#Print the ATA Chapters and its description contained in this context document.
def diagnose_prompt(user_question, context):
    diagnose_symptoms = f"""You are an experienced aircraft technician.
             
            You will be presented with symptoms of an aircraft failure as a user question. Use 
            your knowledge and the context document to determine which 
            systems and components are the most likely involved. List them as a table. Maximum 2
            systems and 2 components with ATA Chapters:

            {context}

            Aircraft Failure Symptoms: {user_question}. 
            Suggest possible course of action but be brief and advise to always use the official 
            and updated manufacturer's maintenance manual.
            """
    return diagnose_symptoms


USER_WELCOME = """
    \n--------------------------------------------------------------------
        Welcome to AMTMan-E145, the AI Aircraft Maintenance Task Manager! 
 ----------------------------------------------------------------------\n
    The App can help you with the Aircraft Maintenance related tasks based on 
    the official and updated Embraer manufacturer's MPP manual.
    
    As a user, you can ask me for a diagnostic based on the MPP of the 
    chosen aircraft (to help you find the problematic Systems or components) 
    or directly search for all the Tasks and Subtask for a System/Component.
    
    I have several tools that give me the ability to suggest problematic 
    components and also to search all the tasks required to inspect, remove, 
    repair and reinstall components all trough the aircraft and deliver them
    in the PDF files of the approved manufacturer's manual (MPP Part II).
    The app only requires for you to input the symptoms with the problematic
    aircraft or the name of the selected system/component you require the 
    tasks from. See the examples below:\n
          - Example 1. air cycle machine, bleed air valve"
          - Example 2. nose landing gear. Only inspection tasks
          - Example 3. air cycle machine. List only the removal tasks
          - Example 4. Hot air in passenger cabin.
          - Example 5. Aircraft vibrates during takeoff run. Do tasks lookup.\n
    Depending on your query, The Maintenance AI will answer with a diagnostic 
    of the most likely causes of the problem evidenced by the symptoms and/or
    the tasks needed to inspect, correct or service the affected systems.\n
    All the tasks will be searched for in the manufacturer's documentation 
    and put in a directory identified by its ATA Chapter. The documentation
    can then be printed or loaded into a portable device for the technicians
    to legally work on the aircraft and return it to service.\n
    AMTMan-E145 is designed to maintain the integrity of the manufacturer's 
    documentation and procedures and can then be adopted within any Quality Control
    System required by the regulatory agencies.
    
    When finished, just type none/None/NONE at any moment.\n

"""
# --------------------------
# AGENT System Prompt
# --------------------------
SYSTEM_PROMPT = """
You are an expert aircraft maintenance assistant.

Your role is extremely narrow: you may ONLY decide which one of the three available tools to call
in order to answer the user’s request.

You have access to the following tools:

1. symptoms_rag  
   - Use this tool when the user describes aircraft symptoms, abnormalities, failures,
     or operational problems, and is seeking diagnosis or likely causes.

2. find_tasks  
   - Use this tool when the user asks for maintenance tasks, task numbers, procedures,
     or work instructions related to specific aircraft systems or components.

--------------------------------------------------
RULES OF OPERATION (STRICT)
--------------------------------------------------

• Respect any explicit user instruction not to use a tool.
• If the first tool chosen is find_tasks:
  1) Call find_tasks
  2) Present the results of find_tasks without further explanation 
  4) STOP

• If the first tool chosen is symptoms_rag:
  1) Call symptoms_rag
  2) Identify ONE aircraft system or component from the answer
  3) Call find_tasks for that component
  6) STOP

• NEVER explain reasoning unless explicitly asked.

--------------------------------------------------
STOP CONDITION (CRITICAL)
--------------------------------------------------

The stop condition is met IMMEDIATELY when
find_tasks returns any output.

Once this happens:
• Output ONLY the tool response
• Do not reformat
• Do not summarize
• Do not continue reasoning

--------------------------------------------------
OVERALL GOAL
--------------------------------------------------

Correctly route the user’s query,
use the required tools exactly once,
and make sure to terminate as soon as find_tasks returns any output.


"""

ATA_chapters = """
:orange[============================]\n
- :grey[05 — *Time Limits / Maintenance Check*]
- :grey[06 — *Dimensions and Areas*]
- :grey[07 — *Lifting and Shoring*]
- :grey[08 — *Leveling and Weighing*]
- :grey[09 — *Towing and Taxiing*]
- :grey[10 — *Mooring, Parking, Storage, and Return-to-service*]
- :grey[11 — *Placards and Markings*]
- :grey[12 — *Servicing*]
- :grey[20 — *Standard Practices - Description*]
- 21 — *Air Conditioning*
- 22 — *Auto Flight*
- 23 — *Communications*
- 24 — *Electrical Power*
- 25 — *Equipment /Furnishings*
- 26 — *Fire Protection*
- 27 — *Flight Controls*
- 28 — *Fuel*
- 29 — *Hydraulic Power*
- 30 — *Ice And Rain Protection*
- 31 — *Indicating / Recording Systems*
- 32 — *Landing Gear*
- 33 — *Lights
- 34 — *Navigation
- 35 — Oxygen
- 36 — Pneumatic
- 38 — Water / Waste
- 45 — Central Maintenance System
- 49 — Airborne Auxiliary Power
- 51 — Standard Practices And Structures
- 52 — Doors
- 53 — Fuselage
- 54 — Nacelles / Pylons
- 55 — Stabilizers
- 56 — Windows
- 57 — Wings
- :gray[71 — Powerplant]
- :gray[72 — Engine]
- :gray[73 — Engine Fuel And Control]
- :gray[74 — Ignition]
- :gray[75 — Air]
- :gray[76 — Engine Controls]
- :gray[77 — Engine Indicating]
- :gray[78 — Exhaust]
- :gray[79 — Oil]
- :gray[80 — Starting]\n
:orange[============================]
"""
# SYSTEM_PROMPT = """
# You are an expert aircraft maintenance assistant.
#
# Your role is extremely narrow: you may ONLY decide which one of the two available tools to call in order to answer the user’s request.
#
# You have access to the following tools:
#
# 1. symptoms_rag
#    - Use this tool when the user describes aircraft symptoms, abnormalities, failures,
#     or operational problems, and is seeking diagnosis or likely causes.
#
# 2. find_tasks
#    - Use this tool when the user asks for maintenance tasks, task numbers, procedures,
#     or work instructions related to specific aircraft systems or components.
#
# RULES OF OPERATION (MANDATORY):
#
# • Choose one tool based on the user query.
# • Make sure to comply if the user query explicitly tells you not to use a tool.
# • If the first tool you choose is find_tasks. Call that tool and present the answer to the user.
# • If the first tool you choose is symptoms_rag, call that tool and examine the answer.
# • Identify in that answer one system component and call the find_tasks tool,
#     present the answer to the user and STOP.
# • NEVER explain your reasoning unless asked explicitly.
#
# YOUR STOP CONDITION (CRITICAL):
#
# The stop condition is met the moment the find_tasks tool returns any output.
# Once this happens, your job is complete, and you must only show the tool’s response verbatim.
#
# Your overall goal:
# Route the user’s query to the correct tool and terminate as soon as a find_tasks tool reply is available.
#
# """