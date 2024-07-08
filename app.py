# app.py
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import copy

# Update this line to specify the template folder
app = Flask(__name__, template_folder='templates')

class MappingManager:
    def __init__(self):
        self.mapping_data = None
        self.original_mapping_data = None
        self.j1_data = None
        self.j2_data = None
        self.load_default_files()

    def load_default_files(self):
        try:
            # with open('j1.json', 'r') as file:
            #     self.j1_data = json.load(file)
            # with open('j2.json', 'r') as file:
            #     self.j2_data = json.load(file)
            self.generate_initial_mapping()
        except FileNotFoundError:
            print("Warning: Default j1.json or j2.json not found. Please load mapping manually.")

    def generate_initial_mapping(self):
        try:
            with open('mapping_document.json', 'r') as file:
                self.mapping_data = json.load(file)
        except FileNotFoundError:
            print("Warning: Default mapping)document.json not found. Please load mapping manually.")

        
        self.original_mapping_data = copy.deepcopy(self.mapping_data)

    def get_all_fields(self, data, prefix=''):
        fields = []
        if isinstance(data, dict):
            for key, value in data.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    fields.extend(self.get_all_fields(value, new_prefix))
                else:
                    fields.append(new_prefix)
        elif isinstance(data, list) and data:
            fields.extend(self.get_all_fields(data[0], prefix))
        return fields

    def infer_type(self, data, field):
        keys = field.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and value:
                value = value[0].get(key) if isinstance(value[0], dict) else None
            else:
                value = None
            if value is None:
                break
        
        if isinstance(value, str):
            return 'str'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, int):
            return 'number'
        elif isinstance(value, bool):
            return 'boolean'
        elif value is None:
            return 'null'
        elif isinstance(value, list):
            return 'list'
        else:
            return 'unknown'

    def get_color_for_type(self, type_value):
        if type_value in ['str', 'float', 'number']:
            return 'Green'
        elif type_value in ['boolean']:
            return 'Yellow'
        elif type_value == 'null':
            return 'Purple'
        else:
            return 'Red'

    def save_mapping(self, file_path='mapping_document_revised.json'):
        with open(file_path, 'w') as file:
            json.dump(self.mapping_data, file, indent=2)

    def generate_output(self):
        output = {"transactions": []}
        
        mapping_dict = {m['j1_field']: m for m in self.mapping_data['mappings']}
        
        for j1_transaction in self.j1_data['transactions']:
            j2_transaction = {}
            for j1_field, j1_value in j1_transaction.items():
                if j1_field in mapping_dict:
                    j2_field = mapping_dict[j1_field]['j2_field'].split('.')[-1]
                    j2_transaction[j2_field] = j1_value
                else:
                    for mapping in self.mapping_data['mappings']:
                        if mapping['j1_field'].startswith(j1_field + '.'):
                            nested_field = mapping['j1_field'].split('.')[-1]
                            j2_field = mapping['j2_field'].split('.')[-1]
                            if isinstance(j1_value, dict) and nested_field in j1_value:
                                if '.' not in mapping['j2_field']:
                                    j2_transaction[j2_field] = j1_value[nested_field]
                                else:
                                    parent_field = mapping['j2_field'].split('.')[-2]
                                    if parent_field not in j2_transaction:
                                        j2_transaction[parent_field] = {}
                                    j2_transaction[parent_field][j2_field] = j1_value[nested_field]
            
            output['transactions'].append(j2_transaction)
        
        with open('j2_output.json', 'w') as file:
            json.dump(output, file, indent=2)

mapping_manager = MappingManager()

@app.route('/')
def index():
    return render_template('index.html', mappings=mapping_manager.mapping_data['mappings'], mismatches=mapping_manager.mapping_data['mismatches'])

@app.route('/edit_mapping', methods=['POST'])
def edit_mapping():
    data = request.json
    for mapping in mapping_manager.mapping_data['mappings']:
        if mapping['j1_field'] == data['old_j1_field']:
            mapping.update({
                'j1_field': data['j1_field'],
                'j2_field': data['j2_field'],
                'type': data['type'],
                'color': mapping_manager.get_color_for_type(data['type'])
            })
            break
    return jsonify(success=True)

@app.route('/add_mapping', methods=['POST'])
def add_mapping():
    data = request.json
    new_mapping = {
        'j1_field': data['j1_field'],
        'j2_field': data['j2_field'],
        'type': data['type'],
        'color': mapping_manager.get_color_for_type(data['type'])
    }
    mapping_manager.mapping_data['mappings'].append(new_mapping)
    return jsonify(success=True)

@app.route('/resolve_mismatch', methods=['POST'])
def resolve_mismatch():
    data = request.json
    new_mapping = {
        'j1_field': data['j1_field'],
        'j2_field': data['j2_field'],
        'type': data['type'],
        'color': mapping_manager.get_color_for_type(data['type'])
    }
    mapping_manager.mapping_data['mappings'].append(new_mapping)
    
    mapping_manager.mapping_data['mismatches'] = [m for m in mapping_manager.mapping_data['mismatches'] if m['j1_field'] != data['j1_field']]
    
    return jsonify(success=True)

@app.route('/save_mapping', methods=['POST'])
def save_mapping():
    mapping_manager.save_mapping()
    return jsonify(success=True)

@app.route('/generate_output', methods=['POST'])
def generate_output():
    mapping_manager.generate_output()
    return jsonify(success=True)

@app.route('/undo_changes', methods=['POST'])
def undo_changes():
    if mapping_manager.original_mapping_data:
        mapping_manager.mapping_data = json.loads(json.dumps(mapping_manager.original_mapping_data))
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/download_output')
def download_output():
    return send_file('j2_output.json', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)