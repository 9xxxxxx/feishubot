import json

def read_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 写入 JSON 文件
def write_config(file_path, config):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)