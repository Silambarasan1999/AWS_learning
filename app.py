from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import ollama
import time

app = Flask(__name__)
CORS(app)

# A dictionary to store conversation history for each user/session
conversation_history = {}

@app.route('/')
def index():
    return render_template('index_1.html')  # Serve the HTML file

@app.route('/query', methods=['POST'])
def query():
    try:
        # Parse the JSON payload from the request
        data = request.get_json()
        user_id = data.get('user_id')  # Expect a consistent user_id from the client
        
        # If no user_id is provided, default to a fixed identifier for testing (or generate one)
        if not user_id:
            user_id = "default_user"  # Replace with a consistent identifier for testing

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
            conversation_history[user_id] = {'user': [], 'llama': []}

        # Append the new user prompt to the conversation history
        conversation_history[user_id]['user'].append(prompt)

        # Build the full conversation context (only include the last user prompt and Llama's last response)
        context = ""
        if conversation_history[user_id]['llama']:
            # Only take the last interaction
            last_llama_response = conversation_history[user_id]['llama'][-1]
            context = f"User: {conversation_history[user_id]['user'][-1]}\nLlama: {last_llama_response}"

        # If the prompt is asking for more details, adjust the context accordingly
        if "tell me about it" in prompt.lower():
            context = f"User: {conversation_history[user_id]['user'][-2]}\nLlama: {conversation_history[user_id]['llama'][-2]}\nUser: {prompt}"

        # Specify the model name (replace 'llama' with your actual model name)
        model_name = 'llama3.2:1b'  # Adjust based on your model

        # Generate response from Llama
        response = ollama.generate(model=model_name, prompt=context)

        # Get the actual response text
        response_text = response.response

        # Add the model's response to the conversation history
        conversation_history[user_id]['llama'].append(response_text)

        # Return the response as JSON
        return jsonify({"response": response_text})

    except Exception as e:
        # Log error details for debugging
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
