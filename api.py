from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import ollama

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file

@app.route('/query', methods=['POST'])
def query():
    try:
        # Parse the JSON payload from the request
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400

        # Specify the model name (replace 'llama' with your actual model name)
        model_name = 'llama3.2:1b'  # Adjust this based on the models available in your system

        # Generate response from Llama
        response = ollama.generate(model=model_name, prompt=prompt)

        # Extract the response content from the 'response' attribute
        response_text = response.response if hasattr(response, 'response') else "No response content found"

        # Return the response as JSON
        return response_text

    except Exception as e:
        # Log error details for debugging
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
