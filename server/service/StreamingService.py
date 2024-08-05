import asyncio
from time import sleep


class StreamRunner:
    def __init__(self, name, loop) -> None:
        self.name = name
        self.loop = loop

    async def start(self):
        print(self.name+" Started!")
        await self.countStart()
            
    async def countStart(self):
        i = 0
        while i < self.loop:
            print(f"looping --->{self.name} - {i}")
            i += 1
            asyncio.sleep(0.1)
        print(self.name + " is completed!")
