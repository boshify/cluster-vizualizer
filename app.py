import streamlit as st
import pandas as pd
import plotly.express as px

# Function to check the presence of required columns in a case-insensitive manner
def columns_present(df, columns):
    df_columns_lower = [col.lower() for col in df.columns]
    return all(col.lower() in df_columns_lower for col in columns)

# Function to load data
@st.cache
def load_data(file):
    return pd.read_csv(file)

# Function to convert dataframe to hierarchical data
def df_to_hierarchy(df):
    hierarchical_data = []
    for _, row in df.iterrows():
        cluster = row['Parent']
        subcluster = row['Cluster']
        page = row['Page Title']
        value = row['Type'] # Consider the 'Type' column as the value for visualization
        
        # Locate cluster
        cluster_idx = next((index for (index, d) in enumerate(hierarchical_data) if d["name"] == cluster), None)
        if cluster_idx is None:
            hierarchical_data.append({"name": cluster, "children": []})
            cluster_idx = len(hierarchical_data) - 1
        
        # Locate subcluster within cluster
        subclusters = hierarchical_data[cluster_idx]["children"]
        subcluster_idx = next((index for (index, d) in enumerate(subclusters) if d["name"] == subcluster), None)
        if subcluster_idx is None:
            subclusters.append({"name": subcluster, "children": []})
            subcluster_idx = len(subclusters) - 1
        
        # Add page data to subcluster
        subclusters[subcluster_idx]["children"].append({"name": page, "value": value})

    return {"name": "root", "children": hierarchical_data}

# Title
st.title("Hierarchical Data Visualization")

# User upload of CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)
    if not columns_present(df, ["Parent", "Cluster", "Page Title", "Type"]):
        st.error("Uploaded CSV is missing one or more required columns: 'Parent', 'Cluster', 'Page Title', 'Type'")
    else:
        hierarchical_data = df_to_hierarchy(df)
        fig = px.sunburst(hierarchical_data, path=['name', 'children', 'children', 'children'], values='value',
                          color='name',
                          color_discrete_map={
                              "root": "lightgray",
                              "Loopio": "#1f77b4",  # Adapt the colors based on the cluster names in the sample CSV
                              # ... add more colors for other clusters if needed
                          })
        st.plotly_chart(fig)

else:
    st.write("Please upload a CSV file.")

