import argparse

from agent import run_agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    args = parser.parse_args()

    result = run_agent(args.user_prompt)
    print(result.answer)
