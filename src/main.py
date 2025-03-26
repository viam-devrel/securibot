import asyncio
from viam.module.module import Module
from models.doorbot import Doorbot


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
