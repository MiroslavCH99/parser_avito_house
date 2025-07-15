import logging

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s  "   
        "[%(levelname)s]  " 
        "%(name)s  "       
        "(module=%(module)s): "
        "%(message)s"
    )
)


logger = logging.getLogger("BaseLogger")
logger.propagate = False