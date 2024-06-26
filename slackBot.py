import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
import dotenv 
dotenv.load_dotenv()

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# When temperature is 0, it will firstly search through cache and return the most confident answer retrieved from cache
# When temperature is between 0 and 2, a higher value will increase the probability of skipping cache search and makes the output more random
# When temperature is at its maximum value of 2, it will skip searching cache and send request to OpenAI directly.
llm = ChatOpenAI(temperature=0)

#template
template = """Your name is BlueBoy, and you are the chatbot in the Slack app. 
Your role is to be an expert in robot development using ROS2. 
People can ask you general questions about robot development, including ROS2. 
Your task is to explain concepts as clearly and understandably as possible, always including usage examples along with simple explanations.

    {history}
    Human: {human_input}
    Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"], 
    template=template
)

chatgpt_chain = LLMChain(
    llm=llm, 
    prompt=prompt, 
    verbose=True, 
    memory=ConversationBufferWindowMemory(k=2),
)

#Event handler for Slack
@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    message = body["event"]['text']

    output = chatgpt_chain.predict(human_input = message)  
    say(output) 

#Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    print(message)
    
    output = chatgpt_chain.predict(human_input = message['text'])   
    say(output)

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()