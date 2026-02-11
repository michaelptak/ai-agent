import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function

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
    for _ in range(10):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            )
        )

        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)

        if not response.usage_metadata:
            raise RuntimeError("The API request failed.")

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        if not response.function_calls:
            print("Response:")
            print(response.text)
            return

        function_results = []
        for function_call in response.function_calls:
            function_call_result = call_function(function_call)
            if not function_call_result:
                raise Exception
            if function_call_result.parts[0].function_response is None:
                raise Exception
            if function_call_result.parts[0].function_response.response is None:
                raise Exception
            function_results.append(function_call_result.parts[0])
            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

        messages.append(types.Content(role="user", parts=function_results))

    print(f"The max number of iterations for the loop was reached.")
    exit(1)

if __name__ == "__main__":
    main()
