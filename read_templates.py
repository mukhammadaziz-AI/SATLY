import os

templates = [
    'app/templates/admin/dashboard.html',
    'app/templates/admin/base.html',
    'app/static/css/admin.css'
]

for t in templates:
    if os.path.exists(t):
        print(f"=== {t} ===")
        with open(t, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print(f"NOT FOUND: {t}")
