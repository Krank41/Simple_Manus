import anthropic
import subprocess

client = anthropic.Anthropic(api_key="paste your key here ")
messagesx = []

def run_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, timeout=10)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

tools = [
    {
        "name": "bash",
        "description": "Run a bash command on the system",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute on the system"
                }
            },
            "required": ["command"]
        }
    }
]


def process_tool_call(tool_name, tool_input):
    if tool_name == "bash":
        return run_bash_command(tool_input["command"])


def calling_claude(role,user_message,assistant_message):
    global messagesx
    
    if role == "user":
        message = user_message
    elif role == "assistant":
        message = assistant_message

    messagesx.append(message)
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4096,
        messages=messagesx,
        tools=tools,
    )
    messagesx.append({"role": "assistant", "content": response.content})
    return response

def chat_with_claude(user_message):
    response = calling_claude("user",{"role": "user", "content": user_message},{})
    print("Simple Manus Intermediate Response:",response.content)
    print("\n \n")
    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input
        tool_result = process_tool_call(tool_name, tool_input)
        content = [{"type":"tool_result" , "tool_use_id": tool_use.id,"content": tool_result}]
        response = calling_claude("user",{"role": "user", "content": content},{})
        print("Simple Manus Intermediate Response:",response.content)
        print("\n \n")
        
    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )
    print(response.content)
    print(f"\nFinal Response : {final_response}")
    return final_response

if __name__ == "__main__":
    print("Welcome to the Terminal Chat Bot! Type 'exit' to quit.")
    while True:
        user_input = input("\nEnter your query: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        try:
            chat_with_claude(user_input)
        except Exception as e:
            print("Exception",e)
