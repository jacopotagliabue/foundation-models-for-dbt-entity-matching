"""

This is a playground for Marvin, to quickly test out functionalities, syntax, the correct
usage of the Marvin API and the connection to OpenAI's API.

"""

from marvin import ai_fn

import asyncio
import concurrent.futures
import multiprocessing as mp
process_pool = concurrent.futures.ProcessPoolExecutor(mp_context=mp.get_context("fork"))

@ai_fn
def list_fruits(n: int) -> list[str]:
    """Generate a list of n fruits"""


if __name__ == "__main__":
    print(list_fruits(n=3))