# orchestrator/orchestrator/metrics.py
from prometheus_client import Counter, Histogram

SAGA_STARTED = Counter(
    "saga_started_total",
    "Nombre de sagas démarrées",
    ["scenario"],    
)

SAGA_COMPLETED = Counter(
    "saga_completed_total",
    "Nombre de sagas terminées avec succès",
    ["scenario"],
)

SAGA_FAILED = Counter(
    "saga_failed_total",
    "Nombre de sagas en échec",
    ["scenario", "stage"],  
)

SAGA_STEP = Counter(
    "saga_step_total",
    "Étapes atteintes dans la saga",
    ["scenario", "step"],   
)

SAGA_DURATION = Histogram(
    "saga_duration_seconds",
    "Durée totale d'une saga (orchestrateur)",
)
