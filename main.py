import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    # Load the API key
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise RuntimeError("No API key found. Add it to the enviornment variable GEMINI_API_KEY.")
    client = genai.Client(api_key=api_key)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Store argument in messages list
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    # Generate the response
    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=messages
    )
    if not response.usage_metadata:
        raise RuntimeError("The API request failed.")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print(response.text)


if __name__ == "__main__":
    main()
