import streamlit as st
import pandas as pd
import numpy as np
import json

st.title("Hierarchical Data Visualization")

# Function to load the uploaded data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df

# Upload widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    df = load_data(uploaded_file)

    # Check if required columns are present
    required_columns = ['cluster', 'subcluster', 'page', 'value']
    if not all(col in df.columns for col in required_columns):
        st.error("Uploaded CSV is missing one or more required columns: 'cluster', 'subcluster', 'page', 'value'")
    else:
        # Convert the dataframe into hierarchical data for the ForceDirectedTree
        def df_to_hierarchy(df):
            data = {}
            for _, row in df.iterrows():
                cluster = row['cluster']
                subcluster = row['subcluster']
                page = row['page']
                value = row['value']

                if cluster not in data:
                    data[cluster] = {}
                if subcluster not in data[cluster]:
                    data[cluster][subcluster] = []

                data[cluster][subcluster].append({"name": page, "value": value})

            # Convert the dictionary to the format suitable for amCharts
            result = []
            for cluster, subclusters in data.items():
                children = []
                for subcluster, pages in subclusters.items():
                    children.append({"name": subcluster, "children": pages})
                result.append({"name": cluster, "children": children})
            return result

        hierarchical_data = df_to_hierarchy(df)

        # Embed the amCharts JavaScript for ForceDirectedTree.
        st.markdown(f"""
            <div id="chartdiv" style="width: 100%; height: 600px;"></div>
            <script src="https://cdn.amcharts.com/lib/4/core.js"></script>
            <script src="https://cdn.amcharts.com/lib/4/charts.js"></script>
            <script>
                am4core.ready(function() {{
                    am4core.useTheme(am4themes_animated);
                    var chart = am4core.create("chartdiv", am4charts.ForceDirectedTree);
                    var networkSeries = chart.series.push(new am4charts.ForceDirectedSeries())

                    chart.data = {json.dumps(hierarchical_data)};

                    networkSeries.dataFields.value = "value";
                    networkSeries.dataFields.name = "name";
                    networkSeries.dataFields.children = "children";
                    networkSeries.nodes.template.tooltipText = "{name}:{value}";
                    networkSeries.nodes.template.fillOpacity = 1;

                    // Add other desired customizations here.

                }});

            </script>
        """, unsafe_allow_html=True)
