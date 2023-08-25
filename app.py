import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    js_code = ""
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            hierarchy_data = process_csv_to_hierarchy(df)
            js_code = generate_js_code(hierarchy_data)
    return render_template('index.html', js_code=js_code)

def process_csv_to_hierarchy(df):
    hierarchy = {'name': 'Root', 'children': []}

    for _, row in df.iterrows():
        try:
            cluster, subcluster, page_title, volume, node_type, url = row['Cluster'], row['Subcluster'], row['Page Title'], row['Volume'], row['Type'], row['URL']

            if not cluster or not subcluster or not page_title:
                continue

            cluster_node = next((child for child in hierarchy['children'] if child['name'] == cluster), None)
            if cluster_node is None:
                cluster_node = {'name': cluster, 'children': [], 'type': node_type}
                hierarchy['children'].append(cluster_node)

            subcluster_node = next((child for child in cluster_node['children'] if child['name'] == subcluster), None)
            if subcluster_node is None:
                subcluster_node = {'name': subcluster, 'children': [], 'type': node_type}
                cluster_node['children'].append(subcluster_node)

            # Ensure there are no duplicate Page Titles
            if not any(child['name'] == page_title for child in subcluster_node['children']):
                subcluster_node['children'].append({'name': page_title, 'value': volume, 'type': node_type, 'url': url})
        except KeyError:
            return "The CSV structure is incorrect. Please check the column names and structure."

    assign_cumulative_values(hierarchy)
    return hierarchy

def assign_cumulative_values(node):
    if 'children' in node:
        total_value = sum(assign_cumulative_values(child) for child in node['children'])
        node['value'] = total_value
        return total_value
    else:
        return node.get('value', 1)

def generate_js_code(hierarchy):
    js_code_cumulative = f'''
    am4core.ready(function() {{
        var chart = am4core.create("chartdiv", am4plugins_forceDirected.ForceDirectedTree);
        chart.zoomable = true;
        var series = chart.series.push(new am4plugins_forceDirected.ForceDirectedSeries());
        series.data = {hierarchy};
        series.dataFields.value = "value";
        series.dataFields.name = "name";
        series.dataFields.children = "children";
        series.dataFields.collapsed = "off";
        series.nodes.template.tooltipText = "{{{{name}}}}: [bold]{{{{value}}}}[/]\\nURL: {{{{url}}}}";
        series.nodes.template.label.text = "{{{{name}}}}";
        series.nodes.template.label.fill = am4core.color("#000");
        series.nodes.template.label.stroke = am4core.color("#FFF");
        series.nodes.template.label.strokeWidth = 0.8;
        series.fontSize = 14;
        series.maxLevels = 2;
        series.minRadius = am4core.percent(0.012);
        series.nodePadding = 5;
        series.manyBodyStrength = -30;
        series.nodes.template.label.hideOversized = false;
        series.nodes.template.label.truncate = false;
        series.nodes.template.events.on("inited", function(event) {{
            var node = event.target;
            if (node.dataItem && node.dataItem.dataContext && node.dataItem.dataContext.type == "New") {{
                var shadow = new am4core.DropShadowFilter();
                shadow.dx = 0;
                shadow.dy = 0;
                shadow.blur = 10;
                shadow.color = am4core.color("#00FF00");
                shadow.opacity = 0.8;
                node.filters.push(shadow);
            }}
        }});
    }});
    '''
    return js_code_cumulative

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
