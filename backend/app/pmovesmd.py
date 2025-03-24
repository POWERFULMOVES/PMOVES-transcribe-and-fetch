import json
import requests
import urllib.parse

def run_vectorshift(prompt):
    # Define the API endpoint and your API key
    url = "https://api.vectorshift.ai/api/pipelines/run"
    api_key = "sk_4jweAOoxmzkZ71pjszp7nx2wt6u9UponG2FcyC7MdHnpsZCx"  # Replace with your actual API key

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Prepare the payload with the user's prompt
    data = {
        "inputs": json.dumps({
            "input_0": prompt  # Use the encoded prompt here
        }),
        "pipeline_id": "67b3349e6cec0d27dd017c5b"
    }

    # Make the POST request to the API
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # This will raise an exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(f"Response content: {response.text}")  # Show detailed error
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    # Ask the user for the prompt input
    user_prompt = input("Enter your prompt: ")
    
    # Add input validation
    if not user_prompt.strip():
        print("Error: Prompt cannot be empty")
        return
        
    # URL encode the prompt
    try:
        encoded_prompt = urllib.parse.quote(user_prompt)
    except Exception as e:
        print(f"Error encoding prompt: {str(e)}")
        return

    # Run the prompt through the Vectorshift API
    output = run_vectorshift(encoded_prompt)  # Pass the encoded prompt
    
    if output is not None:
        # Ask for the markdown file name
        file_name = input("Enter the markdown file name (e.g., output.md): ")
        
        # Save the output into a markdown file with code block formatting
        with open(file_name, "w") as f:
            f.write("```json\n")
            f.write(json.dumps(output, indent=4))
            f.write("\n```")
        print("Output saved to", file_name)

if __name__ == "__main__":
    main()
