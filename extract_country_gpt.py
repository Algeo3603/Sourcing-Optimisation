import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def get_country(address):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON. Given an address string, return a JSON with a single field called 'country' which should contain just the name of the country. Do not use short form for country name. If country is unsure, return None."},
            {"role": "user", "content": f"Return the country of the address '{address}'"}
        ]
    )
    response_json = response.choices[0].message.content
    # print(response_json)
    extracted_country = response.choices[0].message.content.split('"')[-2]
    # print(extracted_location)
    return extracted_country
    