def create_match_details(match_id):
    new_file_name = "pages/" + match_id + ".py"
    search_text = "------------------------------------"
    replace_text = match_id

    with open(r'pages/template.py', 'r') as file:
        data = file.read()
        data = data.replace(search_text, replace_text)
    
    with open(new_file_name, 'w') as file:
        file.write(data)
