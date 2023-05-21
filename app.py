from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = ""

# Create a route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Create a route for handling the OpenAI API requests
@app.route('/get_response', methods=['GET', 'POST'])
def get_response():
    prompt = request.form['prompt']
    response = chat_with_gpt(prompt)  # Use the chat_with_gpt function from the previous examples
    return response


@app.route('/agents')
def agents():
    return render_template('agents.html')


def chat_with_gpt(prompt, model="text-davinci-003", n=1, max_tokens=150):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        n=n,
        max_tokens=max_tokens,
        stop=None,
        temperature=0.7,
    )

    message = response.choices[0].text.strip()
    return message


conversation_history = [
    {
        "role": "system",
        "content": "Please act as a role play agent responsible for coordinating communication between two AI agents with different roles. Facilitate their interactions and ensure they work together effectively to complete the given task."
    }
]


@app.route('/get_response_agents', methods=['POST'])
def get_response_agents():
    role1 = request.form['role1']
    content1 = request.form['content1']
    role2 = request.form['role2']
    content2 = request.form['content2']

    conversation = [
        {'role': 'system',
         'content': 'Please act as a role play agent responsible for coordinating communication between two AI agents with different roles. Facilitate their interactions and ensure they work together effectively to complete the given task. Also provide summary of task and result'},
        {'role': role1, 'content': content1},
        {'role': role2, 'content': content2}
    ]

    response_messages = chat_with_agents_with_iterations(conversation)
    print(f"response messages : {response_messages}")
    formatted_messages = [{"role": message["role"], "content": message["content"]} for message in response_messages]
    print(f"formatted messages : {jsonify(formatted_messages)}")

    return jsonify(formatted_messages)


def chat_with_agents_with_iterations(conversation, model="text-davinci-003", iterations=10):
    messages = conversation

    for i in range(iterations):
        print(f"Iteration {i+1}")

        prompt = "".join([f"{message['role']}: {message['content']}\n" for message in messages])
        print(f"Assistant Prompt: {prompt}")

        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        choice = response.choices[0]
        message = {'role': 'assistant', 'content': choice.text.strip()}
        messages.append(message)

        print(f"Assistant Response: {message['content']}")

        agent_role = messages[-2]['role']
        prompt = "".join([f"{message['role']}: {message['content']}\n" for message in messages])
        print(f"{agent_role} Prompt: {prompt}")

        agent_response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        choice = agent_response.choices[0]
        message = {'role': agent_role, 'content': choice.text.strip()}
        messages.append(message)

        print(f"{agent_role} Response: {message['content']}")

    return messages


if __name__ == '__main__':
    app.run(debug=True)
