from openai import OpenAI
from pathlib import Path
import pandas as pd


client = OpenAI(api_key="")

MODEL="gpt-4o"
file_path = Path('table.xlsx')
df = pd.read_excel(file_path)
content = df.to_string(index=False)

completion = client.chat.completions.create(
  model=MODEL,
  messages=[
    {"role": "system", "content": "Derive as many insights as possible from the excel sheet that I am providing regarding suppliers and buyers. Make them as concise as possible."},
    {"role": "user", "content": content}
  ]
)
print("Assistant: " + completion.choices[0].message.content)