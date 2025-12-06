import React, { useState, useEffect } from 'react';
import SimulationConfigForm from './components/SimulationConfigForm';
import DashboardLayout from './components/DashboardLayout';
import VoxelSliceViewer from './components/VoxelSliceViewer';
import TrendCharts from './components/TrendCharts';
import { SimConfig, SimulationJob, SimulationMetrics } from './types';

const App: React.FC = () => {
  const [jobs, setJobs] = useState<SimulationJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [currentMetrics, setCurrentMetrics] = useState<SimulationMetrics | null>(null);
  const [selectedConfig, setSelectedConfig] = useState<SimConfig | null>(null);
  const [previewData, setPreviewData] = useState<any>(null); // Quick fix type

  const handleStartSimulation = async (config: SimConfig) => {
    setPreviewData(null); // Clear preview when starting
    try {
      const response = await fetch('http://localhost:8000/api/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      const newJob: SimulationJob = await response.json();
      setJobs(prev => [...prev, newJob]);
      setSelectedJobId(newJob.job_id);
      setSelectedConfig(newJob.config);
    } catch (error) {
      console.error("Failed to start simulation", error);
    }
  };

  const handlePreview = async (config: SimConfig) => {
    try {
      const z = Math.floor(config.gridSize / 2);
      const response = await fetch(`http://localhost:8000/api/preview/slice/${z}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      const data = await response.json();
      setPreviewData(data);
    } catch (error) {
      console.error("Failed to generate preview", error);
    }
  };

  const fetchJobStatus = async () => {
    if (!selectedJobId) return;
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${selectedJobId}`);
      const updatedJob: SimulationJob = await response.json();

      setJobs(prev => prev.map(job => job.job_id === updatedJob.job_id ? updatedJob : job));

      if (updatedJob.status === 'running' || updatedJob.status === 'completed') {
        const metricsResponse = await fetch(`http://localhost:8000/api/jobs/${selectedJobId}/metrics`);
        const metrics: SimulationMetrics = await metricsResponse.json();
        setCurrentMetrics(metrics);
      }
    } catch (error) {
      console.error("Failed to fetch job status", error);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
        if (selectedJobId) {
            fetchJobStatus();
        }
    }, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [selectedJobId]);

  return (
    <div className="App" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>NanoSinterWeb</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        <div>
          <SimulationConfigForm onSubmit={handleStartSimulation} onPreview={handlePreview} />
          <DashboardLayout
            jobs={jobs}
            onSelectJob={(id) => {
                setSelectedJobId(id);
                const job = jobs.find(j => j.job_id === id);
                if (job) setSelectedConfig(job.config);
            }}
            selectedJobId={selectedJobId}
          />
        </div>

        <div>
          {previewData && (
             <div style={{ border: '1px dashed #ccc', padding: '1rem', marginBottom: '1rem' }}>
                <h3>Preview (Initial Structure)</h3>
                <canvas
                    width={300}
                    height={300}
                    ref={canvas => {
                        if (canvas && previewData) {
                            const ctx = canvas.getContext('2d');
                            if (ctx) {
                                const [w, h] = previewData.dims;
                                const scale = canvas.width / w;
                                ctx.clearRect(0, 0, w, h);
                                for(let i=0; i<w; i++) {
                                    for(let j=0; j<h; j++) {
                                        const val = previewData.data[i*h+j];
                                        if (val === 0) ctx.fillStyle = '#000';
                                        else ctx.fillStyle = `hsl(${(val * 137) % 360}, 50%, 50%)`;
                                        ctx.fillRect(i*scale, j*scale, scale, scale);
                                    }
                                }
                            }
                        }
                    }}
                />
             </div>
          )}

          {selectedJobId && selectedConfig ? (
            <>
               <h2>Simulating: {selectedJobId.substring(0,8)}...</h2>
               <TrendCharts metrics={currentMetrics} />
               <VoxelSliceViewer jobId={selectedJobId} gridSize={selectedConfig.gridSize} />
            </>
          ) : (
            <p>Select a job or start a new simulation.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
