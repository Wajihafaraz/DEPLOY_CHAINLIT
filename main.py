from agents import Agent , Runner ,OpenAIChatCompletionsModel ,AsyncOpenAI,RunConfig
from openai.types.responses import ResponseTextDeltaEvent

import chainlit as cl
import os
from dotenv import load_dotenv



load_dotenv()


gemini_api_key=os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client

)
Config =RunConfig(
    model = model,
    model_provider = external_client,
    tracing_disabled = True
)

agent = Agent(
    name = "Helper Agent ",
    instructions= "You are a helper agent ",
    model=model

)

# result = Runner.run_sync(
#     agent,
#     input = "hello , how are you?",
#     run_config = Config,
   
# )


# print("Calling")
# print(result.final_output)

# for history saved
@cl.on_chat_start
async def start_message():
#  temporary memory
 cl.user_session.set ("history",[])
 await cl.Message("Hello from Wajiha Faraz , How Can i help you?").send()

 
# event handler jb user msg bhejega chat me to auto ye chalega.
@cl.on_message 
# Ye ek asynchronous function hai jo user ka message handle karega.

async def handle_message(message:cl.Message):
 

 
 history = cl.user_session.get("history")
 
 history.append({"role": "user", "content" : message.content})

# we are adding streaming 
 msg=cl.Message(content="")
 await msg.send()

 result = Runner.run_streamed(
  agent,
  input = history,
  run_config=Config
  
  )
#  now we add functionality for streaming purpose
# streamevents:ek async generator hai jo tumhe AI ke jawab ke parts deta hai live.
 async for event in result.stream_events():
  if event.type=="raw_response_event" and isinstance(event.data , ResponseTextDeltaEvent):
   await msg.stream_token(event.data.delta)
  

 history.append({"role":"assistant","content":result.final_output})
 cl.user_session.set("history",history)
 await cl.Message(content = result.final_output).send()
 