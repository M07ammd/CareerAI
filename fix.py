import os
for root, _, files in os.walk('tests'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as file:
                data = file.read()
            data = data.replace('"backend.', '"app.')
            data = data.replace("'backend.", "'app.")
            with open(p, 'w', encoding='utf-8') as file:
                file.write(data)
