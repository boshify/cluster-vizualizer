import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
latest_hierarchy = None  # global variable to store the latest processed data

@app.route('/', methods=['GET', 'POST'])
def index():
    global latest_hierarchy
    if request.method == 'POST':
        file = request.files['file']
        if file:
            latest_hierarchy = process_file(file)
    return render_template('index.html')

@app.route('/get-data', methods=['GET'])
def get_data():
    global latest_hierarchy
    return jsonify(latest_hierarchy)

def process_file(file):
    df = pd.read_csv(file)
    hierarchy = {
        "name": "Root",
        "children": []
    }
    for _, row in df.iterrows():
        insert_data(hierarchy, row['Cluster 1'], row['Cluster 2'], row['Keyword'], row['Volume'], row['URL'], row['New/Existing'])
    assign_cumulative_values(hierarchy)
    return hierarchy

def insert_data(hierarchy, cluster1, cluster2, keyword, volume, url, type):
    cluster1_node = next((item for item in hierarchy["children"] if item["name"] == cluster1), None)
    if not cluster1_node:
        cluster1_node = {
            "name": cluster1,
            "children": [],
            "type": type
        }
        hierarchy["children"].append(cluster1_node)

    cluster2_node = next((item for item in cluster1_node["children"] if item["name"] == cluster2), None)
    if not cluster2_node:
        cluster2_node = {
            "name": cluster2,
            "children": [],
            "type": type
        }
        cluster1_node["children"].append(cluster2_node)

    keyword_node = {
        "name": keyword,
        "value": volume,
        "url": url,
        "type": type
    }
    cluster2_node["children"].append(keyword_node)

def assign_cumulative_values(node):
    if "children" not in node:
        return node["value"]
    else:
        sum_values = 0
        for child in node["children"]:
            sum_values += assign_cumulative_values(child)
        node["value"] = sum_values
        return sum_values

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
