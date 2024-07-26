def split_file(input_file, char_limit=100000):
    try:
        # Read the entire content of the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split the content into chunks of char_limit size
        parts = [content[i:i + char_limit] for i in range(0, len(content), char_limit)]
        
        # Write each part to separate output files
        for idx, part in enumerate(parts):
            output_file = f'op{idx + 1}.txt'
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(part)
        
        print(f"Successfully split {input_file} into {len(parts)} parts.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

input_file = 'input.txt'
split_file(input_file)