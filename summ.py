from openai import OpenAI
from pathlib import Path
import pandas as pd


client = OpenAI(api_key="")

MODEL="gpt-4o"
file_path = Path('Brake Line.xlsx')
df = pd.read_excel(file_path)
df=df.sample(n=400)
content = df.to_string(index=False)

prompt="""You are an expert data analyst who specializes in deriving insights from large excel sheets.
Your task is to identify as many insights as possible regarding industry trends, suppliers, buyers and partnerships between suppliers and buyers from the excel sheet being provided to you as well as any other information that you have access to.
Divide your response into sections.

When highlighting an insight:
1) Give it a short title, and follow it up with concise sentence that gives further details on the next line.
2) There should be no formatting
3) Do not make the insights too long

Your goal is to help your client make smarter decisions regarding their business using this data.
"""

completion = client.chat.completions.create(
  model=MODEL,
  messages=[
    {"role": "system", "content": prompt},
    {"role": "user", "content": content}
  ]
)
print(completion.choices[0].message.content)