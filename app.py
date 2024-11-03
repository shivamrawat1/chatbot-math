from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import time

app = Flask(__name__)

# Replace with your OpenAI API key
client = OpenAI(api_key='')

# Create an Assistant using the Assistants API
try:
    assistant = client.beta.assistants.create(
        name="Math Tutor",
        instructions="You are a personal math tutor. Write and run code to answer math questions.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",  # Use an available model
    )
    print(f"Assistant created with ID: {assistant.id}")
except Exception as e:
    print(f"Error creating assistant: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']
    print(f"Received user message: {user_message}")

    try:
        # Create a new thread with the user's message
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        print(f"Thread created with ID: {thread.id}")

        # Run the assistant on the thread
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        print(f"Run started with ID: {run.id}")

        # Poll the run until it completes or fails
        max_retries = 30
        retries = 0
        while run.status not in ['completed', 'failed', 'cancelled', 'incomplete'] and retries < max_retries:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
            print(f"Polling run status: {run.status}")
            retries += 1

        if run.status == 'completed':
            # Retrieve the assistant's reply
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            print(f"Messages retrieved: {messages.data}")

            # Find the assistant's messages
            assistant_messages = [msg for msg in messages.data if msg.role == 'assistant']
            if assistant_messages:
                assistant_reply = assistant_messages[-1]  # Get the last assistant message
                # Extract the text content from the message
                assistant_message = ''
                for content_item in assistant_reply.content:
                    if content_item.type == 'text':
                        assistant_message += content_item.text.value
                print(f"Assistant's response: {assistant_message}")
                return jsonify({'message': assistant_message})
            else:
                print("No assistant response found.")
                return jsonify({'message': 'No assistant response found.'}), 500
        else:
            print(f"Error: Run status is {run.status} after polling.")
            return jsonify({'message': f'Error: Run status is {run.status}.'}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
