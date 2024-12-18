from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import ollama

app = Flask(__name__)
CORS(app)

# A dictionary to store conversation history for each user/session
conversation_history = {}

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file

@app.route('/query', methods=['POST'])
def query():
    try:
        # Parse the JSON payload from the request
        data = request.get_json()
        user_id = data.get('user_id', 'default')  # Use a user_id to identify the user/session
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400

        # Handle "clear all" command to reset user's conversation history
        if prompt.lower() == "clear all":
            if user_id in conversation_history:
                del conversation_history[user_id]
                return jsonify({"response": "Your conversation history has been cleared."})
            else:
                return jsonify({"response": "No conversation history found to clear."})

        # Initialize conversation history for the user if not already done
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Append the new prompt to the conversation history
        conversation_history[user_id].append({"role": "user", "content": prompt})

        # Build the full conversation context
        context = "\n".join(
            f"{entry['role']}: {entry['content']}" for entry in conversation_history[user_id]
        )

        # Specify the model name (replace 'llama' with your actual model name)
        model_name = 'llama3.2:1b'  # Adjust based on your model

        # Generate response from Llama
        response = ollama.generate(model=model_name, prompt=context)

        # Get the actual response text
        response_text = response.response

        # Add the model's response to the conversation history
        conversation_history[user_id].append({"role": "llama", "content": response_text})

        # Return the response as JSON
        return jsonify({"response": response_text})

    except Exception as e:
        # Log error details for debugging
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
