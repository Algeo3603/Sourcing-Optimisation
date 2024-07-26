import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

query="Who are the biggest suppliers of shock absorbers?"
with open('op1.txt','r')as file:
    text=file.read()

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an expert analyst whose goal is to answer the queries asked by the user, based on the information given to you."},
        {"role": "user", "content": "The information provided to you is:\n"+text+"The user query is:\n"+query}
    ]
)
resp=response.choices[0].message.content
print(resp)