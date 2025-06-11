from .core.db import db_cl
from fastapi import FastAPI
from .core.config import config
from .rabbit.client import mq_cl
from .k8.client import k8_cl
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    # everything before yield is executed before the app starts up

    # set up rabbit
    # await mq_cl.connect(str(config.RABBIT_URI))
    # await mq_cl.setup_rpc_queues()

    # set up db
    db_cl.connect(str(config.DB_URI))

    # load kubernetes client
    k8_cl.load_service_account()

    # create tables
    await db_cl.init_db()

    yield
    
    # everything after yield is execute after the app shuts down
    # await mq_cl.disconnect()
    await db_cl.disconnect()


if not config.CI:
    app = FastAPI(
        title=config.TITLE,
        lifespan=lifespan
    )
else:
    app = FastAPI(
        title=config.TITLE
    )



# from .routes.listings import listings_router
from .routes.gameservers import gameservers_router
from .routes.ping import healthcheck_router


# app.include_router(listings_router, prefix="/listings")
app.include_router(gameservers_router, prefix="/gameservers")
app.include_router(healthcheck_router, prefix="/healthcheck")