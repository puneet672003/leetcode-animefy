from mangum import Mangum
from core.server import Server

app = Server.create_app()
handler = Mangum(app, lifespan="off")
