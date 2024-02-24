def create_match_details(match_id):
    file_name = match_id + ".py"

    with open(file_name, "w") as f:
        f.write('')