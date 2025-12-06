import React, { useState, useEffect } from 'react';
import { SimulationJob } from '../types';

interface Props {
  jobs: SimulationJob[];
  onSelectJob: (jobId: string) => void;
  selectedJobId: string | null;
}

const DashboardLayout: React.FC<Props> = ({ jobs, onSelectJob, selectedJobId }) => {
  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', marginTop: '1rem' }}>
      <h3>Job Dashboard</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ textAlign: 'left' }}>
            <th>Job ID</th>
            <th>Status</th>
            <th>Steps</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map(job => (
            <tr key={job.job_id} style={{ backgroundColor: selectedJobId === job.job_id ? '#e0e0e0' : 'transparent' }}>
              <td>{job.job_id.substring(0, 8)}...</td>
              <td>{job.status}</td>
              <td>{job.current_step} / {job.total_steps}</td>
              <td>
                <button onClick={() => onSelectJob(job.job_id)}>View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DashboardLayout;
