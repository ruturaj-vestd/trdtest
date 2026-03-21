from __future__ import annotations

import argparse
import asyncio

from graph import ResearchGraph


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ticker", required=True)
    args = p.parse_args()
    state = asyncio.run(ResearchGraph().run_for_ticker(args.ticker))
    print(state.markdown_report)


if __name__ == "__main__":
    main()
