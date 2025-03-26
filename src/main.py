import asyncio
from viam.module.module import Module
try:
    from models.doorbot import Doorbot
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.doorbot import Doorbot


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
