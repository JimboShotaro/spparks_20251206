from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum

class SimConfig(BaseModel):
    grid_size: int = 50  # Reduced default for prototype performance
    temperature: float = 1.0
    initial_porosity: float = 0.30
    event_ratios: Dict[str, float] = {"growth": 2.0, "migration": 1.0, "annihilation": 4.0}
    num_seeds: Optional[int] = 20

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SimulationJob(BaseModel):
    job_id: str
    config: SimConfig
    status: JobStatus
    current_step: int = 0
    total_steps: int = 0
    created_at: float
