export interface SimConfig {
  gridSize: number;
  temperature: number;
  initialPorosity: number;
  eventRatios: {
    growth: number;
    migration: number;
    annihilation: number;
  };
  numSeeds?: number;
}

export interface SimulationJob {
  job_id: string;
  config: SimConfig;
  status: 'pending' | 'running' | 'completed' | 'failed';
  current_step: number;
  total_steps: number;
  created_at: number;
}

export interface SimulationMetrics {
  mcs: number;
  density: number;
  corrected_radius: number;
  num_clusters: number;
  porosity: number;
}

export interface VoxelData {
  dims: [number, number];
  data: number[];
}
