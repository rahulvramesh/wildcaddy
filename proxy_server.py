import asyncio
from aiohttp import web, ClientSession, TCPConnector
from PyQt6.QtCore import QThread, pyqtSignal

class ProxyServer(QThread):
    server_started = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.app = web.Application()
        self.app.router.add_route('*', '/{path:.*}', self.handle)
        self.routes = {}
        self.loop = None
        self.runner = None

    async def handle(self, request):
        host = request.headers.get('Host')
        if host in self.routes:
            target = self.routes[host]
            url = f"{target}{request.path_qs}"
            headers = dict(request.headers)
            headers.pop('Host', None)

            async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                try:
                    async with session.request(
                            method=request.method,
                            url=url,
                            headers=headers,
                            data=await request.read(),
                            allow_redirects=False,
                    ) as resp:
                        headers = dict(resp.headers)
                        headers.pop('Transfer-Encoding', None)

                        return web.StreamResponse(
                            status=resp.status,
                            headers=headers
                        ).send_headers(
                        ).write(
                            await resp.read()
                        )
                except Exception as e:
                    return web.Response(text=f"Error: {str(e)}", status=500)
        return web.Response(text="Not Found", status=404)

    def add_route(self, domain, target):
        self.routes[domain] = target

    def remove_route(self, domain):
        if domain in self.routes:
            del self.routes[domain]

    def get_routes(self):
        return self.routes

    async def start_server(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', 80)
        await site.start()
        print("Proxy server started on http://localhost:80")
        self.server_started.emit()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())
        self.loop.run_forever()

    def stop(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.runner:
            self.loop.run_until_complete(self.runner.cleanup())