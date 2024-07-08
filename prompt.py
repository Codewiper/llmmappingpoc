import json
import openai

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_fields(json_obj, parent_key='', field_list=None):
    if field_list is None:
        field_list = []

    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            field_list.append((full_key, type(v).__name__))
            extract_fields(v, full_key, field_list)
    elif isinstance(json_obj, list):
        for item in json_obj:
            extract_fields(item, parent_key, field_list)

    return field_list

def get_field_mappings(fields_j1, fields_j2):
    prompt = """
You are provided with two sets of fields from different JSON files. Your task is to map the fields from both sets and classify them with color codes according to the following rules:

### Rules:
1. **Green**: Both fields have the same name and data type.
2. **Yellow**:
    - Fields have the same name but different data types.
    - Fields have different names but the same data type.
    - Fields have similar names and the same or different data types (e.g., `currency` vs. `currency_code`).
3. **Red**:
    - No corresponding field in the other JSON.
    - Data types cannot be reconciled.
    - Any discrepancies that cannot be categorized as Green or Yellow.

### Provide the mapping in the following format:
[
  {"j1_field": "", "j2_field": "", "type": "", "color": ""},
  ...
]

### Fields from j1.json:
""" + "\n".join([f"{field[0]} ({field[1]})" for field in fields_j1]) + """

### Fields from j2.json:
""" + "\n".join([f"{field[0]} ({field[1]})" for field in fields_j2]) + """
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0
    )

    # Debug print the raw response content
    response_content = response.choices[0].message['content'].strip()
    response_content = response_content.strip("`json\n").strip("\n`").replace("\n","")
    print("Raw LLM Response:\n", response_content)

    # Check if the response is valid JSON
    try:
        return json.loads(response_content)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON response:", e)
        return None

def separate_mappings(mappings):
    if mappings is None:
        return {"mappings": [], "mismatches": []}

    final_mappings = {"mappings": [], "mismatches": []}
    mapped_fields = set()

    for mapping in mappings:
        j1_field = mapping["j1_field"]
        color = mapping["color"].lower()

        if color in ["green", "yellow"]:
            final_mappings["mappings"].append(mapping)
            mapped_fields.add(j1_field)
        elif color == "red" and j1_field not in mapped_fields:
            final_mappings["mismatches"].append({
                "j1_field": mapping["j1_field"],
                "j1_type": mapping["type"],
                "color": mapping["color"]
            })

    return final_mappings

def generate_mapping_document(mapping_document):
    with open('mapping_document.json', 'w') as file:
        json.dump(mapping_document, file, indent=2)

def main():
    """Main function to execute the program."""

    # Read and parse JSON files
    j1 = read_json('j1.json')
    j2 = read_json('j2.json')

    # Extract fields
    fields_j1 = extract_fields(j1)
    fields_j2 = extract_fields(j2)

    # Get field mappings using LLM
    field_mappings = get_field_mappings(fields_j1, fields_j2)

    # Separate mappings and mismatches
    final_mapping_document = separate_mappings(field_mappings)

    # Generate mapping document
    generate_mapping_document(final_mapping_document)

if __name__ == '__main__':
    main()
