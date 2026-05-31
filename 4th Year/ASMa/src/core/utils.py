import logging
from datetime import datetime
from core.config import LOG_LEVEL, LOG_FILE

# Configurar logging
def setup_logger(name: str = "SMA_SAUDE") -> logging.Logger:
    """Configura e retorna um logger."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Handler para ficheiro
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(getattr(logging, LOG_LEVEL))
    
    # Handler para console
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, LOG_LEVEL))
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger


# Logger global
logger = setup_logger()

# Funções de tempo
def get_current_time() -> str:
    """Retorna timestamp atual em ISO format."""
    return datetime.now().isoformat()

# Funções de formatação
def format_emergency_id(patient_id: str, timestamp: str) -> str:
    """Gera ID único para emergência."""
    clean_time = timestamp.replace(":", "").replace("-", "").replace(".", "")
    return f"EMG_{patient_id}_{clean_time}"
