import logging
import avalon.api
import avalon.nuke

logging.getLogger("").setLevel(20)  # INFO level
avalon.api.install(avalon.nuke)
