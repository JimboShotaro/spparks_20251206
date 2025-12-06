from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models import SimConfig, SimulationJob, JobStatus
from ..core.simulation import SimulationContext, PottsGrowthModel, SGGSSinteringStrategy
from ..core.analysis import MicrostructureAnalyzer
import uuid
import time
import os
import numpy as np

router = APIRouter()

# In-memory storage for jobs (replace with DB/Redis in production)
jobs = {}
sim_contexts = {}

@router.post("/jobs", response_model=SimulationJob)
async def create_job(config: SimConfig, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job = SimulationJob(
        job_id=job_id,
        config=config,
        status=JobStatus.PENDING,
        created_at=time.time()
    )
    jobs[job_id] = job

    # Initialize simulation context
    if config.event_ratios.get("growth", 0) > 0:
        # Simplified strategy selection logic
        strategy = PottsGrowthModel()
    else:
        strategy = SGGSSinteringStrategy(config.event_ratios)

    sim_contexts[job_id] = SimulationContext(config, strategy)

    # Start worker task
    background_tasks.add_task(run_simulation, job_id)

    return job

@router.get("/jobs/{job_id}", response_model=SimulationJob)
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@router.post("/preview/slice/{z}")
async def get_preview_slice(config: SimConfig, z: int):
    """
    Generate a preview of the initial microstructure based on config.
    Returns the slice data without creating a job.
    """
    # Use SGGSSinteringStrategy to generate the grid as it handles both growth and porosity
    strategy = SGGSSinteringStrategy(config.event_ratios)
    grid = strategy.initialize_grid(config)

    if z < 0 or z >= grid.shape[2]:
        raise HTTPException(status_code=400, detail="Z index out of bounds")

    slice_data = grid[:, :, z].flatten().tolist()
    return {"dims": [grid.shape[0], grid.shape[1]], "data": slice_data}

@router.get("/jobs/{job_id}/slice/{z}")
async def get_slice(job_id: str, z: int):
    if job_id not in sim_contexts:
        raise HTTPException(status_code=404, detail="Job context not found")

    context = sim_contexts[job_id]
    grid = context.grid

    if z < 0 or z >= grid.shape[2]: # Assuming Z is axis 2
         raise HTTPException(status_code=400, detail="Z index out of bounds")

    # Return slice data (flattened for JSON)
    slice_data = grid[:, :, z].flatten().tolist()
    return {"dims": [grid.shape[0], grid.shape[1]], "data": slice_data}

@router.get("/jobs/{job_id}/metrics")
async def get_metrics(job_id: str):
    if job_id not in sim_contexts:
         raise HTTPException(status_code=404, detail="Job context not found")

    context = sim_contexts[job_id]
    metrics = MicrostructureAnalyzer.calculate_true_metrics(context.grid)
    metrics["mcs"] = context.step
    return metrics

def run_simulation(job_id: str):
    job = jobs[job_id]
    job.status = JobStatus.RUNNING
    context = sim_contexts[job_id]

    try:
        # Simulate for some steps
        target_steps = 100 # Short run
        job.total_steps = target_steps

        for i in range(target_steps):
            context.execute_step()
            job.current_step = i + 1
            # Sleep to simulate work if needed, or just run
            # time.sleep(0.1)

        job.status = JobStatus.COMPLETED
        # Save final result
        result_path = f"results/{job_id}.npy"
        os.makedirs("results", exist_ok=True)
        context.save_snapshot(result_path)
        job.result_path = result_path

    except Exception as e:
        job.status = JobStatus.FAILED
        print(f"Job {job_id} failed: {e}")
