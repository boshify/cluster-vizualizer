from flask import Flask, render_template, request
import pandas as pd
import json

app = Flask(__name__)

def insert_data(hierarchy, cluster, subcluster, keyword, volume, url, type):
    if cluster not in hierarchy:
        hierarchy[cluster] = {"name": cluster, "children": [], "type": "Existing", "value": 0}
    if subcluster:
        subclusters = [child for child in hierarchy[cluster]["children"] if child["name"] == subcluster]
        if not subclusters:
            hierarchy[cluster]["children"].append({"name": subcluster, "children": [], "type": "Existing", "value": 0})
            subclusters = [child for child in hierarchy[cluster]["children"] if child["name"] == subcluster]
        subclusters[0]["children"].append({"name": keyword, "value": volume, "type": type, "url": url})
        subclusters[0]["value"] += volume
    else:
        hierarchy[cluster]["children"].append({"name": keyword, "value": volume, "type": type, "url": url})
    hierarchy[cluster]["value"] += volume

def process_file(file):
    hierarchy = {}
    df = pd.read_csv(file)
    for _, row in df.iterrows():
        insert_data(hierarchy, row['Cluster'], row['Subcluster'], row['Page Title'], row['Volume'], row['URL'], row['Type'])
    return {"name": "Root", "children": [value for key, value in hierarchy.items()], "value": sum([value["value"] for key, value in hierarchy.items()])}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        latest_hierarchy = process_file(file)
        return render_template('index.html', hierarchy=json.dumps(latest_hierarchy))
    return render_template('index.html', hierarchy=None)

if __name__ == "__main__":
    app.run(debug=True)
