import os
import requests
from dotenv import load_dotenv

load_dotenv()

from smolagents import tool, ToolCallingAgent, DuckDuckGoSearchTool, LiteLLMModel
from tools.odds_download_tool import odds_download_tool

def chunk_response(text, max_length=2000) -> list[str]:
    """  Splits a string into chunks of a maximum length, preferably at newlines.

    Args:
        text: The string to split
        max_length: The max length of each chunk (default: 2000)

    Returns:
        A list of strings
    """
    chunks = []
    current_chunk = ""

    for line in text.splitlines(keepends=True):
        if len(current_chunk) + len(line) <= max_length:
            current_chunk += line
        else:
            chunks.append(current_chunk)
            current_chunk = line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def create_predictions():
    try:

        model = LiteLLMModel(model_id="gpt-4o-mini")
        agent = ToolCallingAgent(tools=[DuckDuckGoSearchTool(), odds_download_tool], model=model, add_base_tools=True, planning_interval=3, max_steps=10)

        query = """
        What teams are most likely to win this week's NRL matches (2025 season), first use odds_download_tool
        to get a list of matches and current odds, use the commence_time value to get the date of the match
        and find out the current round number, and then also search for commentator and public opinion on the
        matches (verify current round and season with the seaches). Please give a brief summary of opinion with
        each prediction and write in the style of Reg Reagan with plenty of biff. Please predict all matches
        listed in the odds_download_tool. Don't mention the name Reg Reagan and provide a concise final answer
        in format: Intro [**Match** - Odds\nSummary\nPrediction] Outro
        """

        response = agent.run(query)

        #response = "Test"
        if response is not None:

            response_chunks = chunk_response(response)

            for chunk in response_chunks:
                data = {"content": str(chunk)}
                
                if os.environ.get('DISCORD_WEBHOOK') is not None:
                    requests.post(os.environ.get('DISCORD_WEBHOOK'), json=data, timeout=5)

            print(response)
        else:
            raise Exception("No response")

    except Exception as e: 
        error = {"content": str(e)}
        if os.environ.get('DISCORD_DEBUG_WEBHOOK') is not None:
            requests.post(os.environ.get('DISCORD_DEBUG_WEBHOOK'), json=error, timeout=3)

        print(e)

def handler(event, context):
    """ Handler to run in AWS lambdas"""
    create_predictions()

if __name__ == "__main__":
    create_predictions()
