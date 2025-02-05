import json

class DataManager:
    def __init__(self):
        self.proxies_path = "data/proxies"

    def write_to_file_txt(self, file_path, data):
        file = open(file_path, "w")
        for d in data:
            file.write(d + "\n")
        file.close()

    def get_data_from_file_json(self, path):
        with open(path, 'r') as file:
            data = json.load(file)
        return data

    def get_proxy(self):
        with open(self.proxies_path, 'r') as file:
            data = [row.strip() for row in file]
            proxy = data.pop(0)
            self.write_to_file_txt(self.proxies_path, data)
            return proxy
