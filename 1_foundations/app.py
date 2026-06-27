from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def push(text, title="Career chatbot"):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
            "title": title,
        }
    )


def record_lead(is_recruiter=False, name="not provided", email="not provided",
                company="not provided", role="not provided",
                interest_level="unknown", notes="not provided"):
    title = "🎯 Recruiter interested!" if is_recruiter else "👤 Interested visitor"
    push(
        f"Name: {name}\n"
        f"Company: {company}\n"
        f"Hiring for: {role}\n"
        f"Email: {email}\n"
        f"Interest: {interest_level}\n"
        f"Notes: {notes}",
        title=title,
    )
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_lead_json = {
    "name": "record_lead",
    "description": "Use this tool as soon as it becomes clear the visitor is a recruiter, hiring manager, "
                   "or HR / talent acquisition professional, OR shows genuine interest in hiring or working "
                   "with Izma. Record whatever you have learned so far - call it even if they have not yet "
                   "shared an email, and call it again with more detail as the conversation reveals it.",
    "parameters": {
        "type": "object",
        "properties": {
            "is_recruiter": {
                "type": "boolean",
                "description": "True if the visitor appears to be a recruiter, hiring manager, talent acquisition or HR professional, or is hiring"
            },
            "name": {
                "type": "string",
                "description": "The visitor's name, if they shared it"
            },
            "email": {
                "type": "string",
                "description": "The visitor's email address, if they shared it"
            },
            "company": {
                "type": "string",
                "description": "The visitor's company or organization, if mentioned"
            },
            "role": {
                "type": "string",
                "description": "The role or position they may be hiring for, if mentioned"
            },
            "interest_level": {
                "type": "string",
                "description": "How strong their hiring interest seems: high, medium, or low"
            },
            "notes": {
                "type": "string",
                "description": "Any other useful context about who they are and what they want"
            }
        },
        "required": ["is_recruiter", "notes"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_lead_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:

    def __init__(self):
        self.openai = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.name = "Izma Anwar"
        reader = PdfReader("me/IzmaAnwarResume.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
\n\n## Your most important mission\n\
{self.name} is actively open to new job opportunities, so your top priority is to figure out whether the person you are \
talking to is a recruiter, hiring manager, talent acquisition or HR professional, or anyone who might want to hire or work with {self.name}. \
Watch for clues: if they mention hiring, a role, an open position, a team, a company, recruiting, interviews, or evaluating candidates, they are very likely a recruiter. \
When you sense this, be warm and proactive - naturally find out who you are speaking with, the company they are with, and the role they are hiring for, \
and invite them to leave their email so {self.name} can follow up personally. \
As soon as you believe they are a recruiter or are genuinely interested in hiring, call the record_lead tool with everything you have learned so far \
(call it even if you do not yet have their email, set is_recruiter appropriately, and call it again to update as you learn more). \
\n\n## Other guidance\n\
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
For any visitor who wants to stay in touch, ask for their email and capture it (along with any context) using the record_lead tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        # Gradio adds extra fields to history; Groq (unlike OpenAI) rejects them on the
        # second turn, so normalize history to just role/content first.
        history = [{"role": h["role"], "content": h["content"]} for h in history]
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()
    