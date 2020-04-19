from syncit import Syncit

class Server():
    """
    Class for the server actions.

    Attributes:
        connected (set): Set of tuples, containing connected clients and the next expected message from the client.

    """
    def __init__(self):
        self.connected = set()  


    def start_server(self):
        """
        Starts the server.
        """
        self.websockets.serve(self.handler, "localhost", 5000)
        asyncio.get_event_loop().run_until_complete(server.start_server)
        asyncio.get_event_loop().run_forever()


    def handler(self, websocket, path):
        this.connected.add(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            this.connected.remove(websocket)
    
    def handle_message(websocket, message):
        json_msg = json.loads(message)
        action = json_msg["action"]
        
        if(action == '')
        
