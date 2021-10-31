import aiohttp

class LoopbackRequestProvider(object):
    async def get(self, path, on_finish):
        async with aiohttp.ClientSession() as session:
            async with session.get(path) as res:
                # Note: There is probably a better way to pass this back apart from doing a callback
                # Just awaiting get() results in session closed
                output = await on_finish(res)
                await session.close()
                return output