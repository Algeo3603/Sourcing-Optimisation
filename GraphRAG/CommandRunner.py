import subprocess
query="You are an expert car industry analyst with vast knowledge about car part supplier companies and car part manufacturer groups. Your goal is to answer the given query to the best of your abilities using both the provided data and any other data you have.If you do not know the answer to a given query, state that you do not have sufficient information. You are to strictly answer according to the specified format. The query is:Identify all the supplier manufacturing groups using the given data. Response Format:Group Name: XYZ Group(new line)Subsidiary Companies: Subsidiary Company 1,(new line)Subsidiary Company 2,(new line)Subsidiary Company 3   Example:Group Name: ZF Group (new line) Subsidiary Companies:ZF Automotive Components & Systems (Shanghai) Co., Ltd. , (new line)ZF Chassis Systems (Beijing) Co., Ltd. , (new line)ZF FAWER Chassis Technology (Changchun) Co., Ltd.  Ensure your response adheres strictly to the given format. Do not add any unnecessary decorations to the response like # or * . Include all relevant information available."
command='py -m graphrag.query --root . --method global ' + '"' + query + '"'

# print(command)
# exit()


result = subprocess.run(command, shell=True, capture_output=True, text=True)

print("Output:\n", result.stdout)