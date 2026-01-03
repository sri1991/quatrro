import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_object: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_object)

def setup_logging(level: str = "INFO"):
    """
    Configures the root logger to use JSONFormatter.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
        
    # Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JSONFormatter())
    logger.addHandler(stream_handler)
    

    
    # Set levels for some noisy libraries if needed
    logging.getLogger("uvicorn.access").disabled = True # Disable default access log to use our middleware
    logging.getLogger("multipart").setLevel(logging.WARNING)
