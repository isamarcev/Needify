# from settings import settings

bind = "0.0.0.0:8020"
timeout = 0
loglevel = "debug"
worker_class = "uvicorn.workers.UvicornWorker"

workers = 1
# if settings.settings_module == "dev":
reload = True
