from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            data = process_file(file)
    return render_template('index.html', data=data)

def process_file(file):
    # Read the uploaded file directly
    df = pd.read_csv(file)
    
    # ... [Your processing code here] ...

    return hierarchy

if __name__ == "__main__":
    app.run(debug=True)
