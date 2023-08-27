from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Variable to cache the latest hierarchy data
latest_hierarchy_data = None

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
    
    # Convert all column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Check if necessary columns are present
    required_columns = ['cluster', 'subcluster', 'page title', 'volume', 'url', 'type']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Uploaded CSV is missing the required column: '{col}' (considering case-insensitive match)")

    for _, row in df.iterrows():
        insert_data(hierarchy, row['cluster'], row['subcluster'], row['page title'], row['volume'], row['url'], row['type'])
    return {"name": "Root", "children": [value for key, value in hierarchy.items()], "value": sum([value["value"] for key, value in hierarchy.items()])}

@app.route('/', methods=['GET', 'POST'])
def index():
    global latest_hierarchy_data
    if request.method == 'POST':
        file = request.files.get('file')
        latest_hierarchy_data = process_file(file)
        return render_template('index.html', hierarchy=json.dumps(latest_hierarchy_data))
    return render_template('index.html', hierarchy=None)

@app.route('/get-data', methods=['GET'])
def get_data():
    return jsonify(latest_hierarchy_data)

if __name__ == "__main__":
    app.run(debug=True)
