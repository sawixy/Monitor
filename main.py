import asyncio
from dotenv import load_dotenv
import sys
from systems.config.config import Config

class App:
    def __init__(self, config_path):
        from systems.config.config import ConfigFactory
        self.config_factory = ConfigFactory()

async def main():
    pass

if __name__ == "__main__":
    load_dotenv()

    app = App
    if len(sys.argv) > 1:
        app = App(sys.argv[1])
    else:
        raise ValueError("config path not found")

    asyncio.run(main())