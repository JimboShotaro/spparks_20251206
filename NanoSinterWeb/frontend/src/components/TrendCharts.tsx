import React from 'react';
import { SimulationMetrics } from '../types';

interface Props {
  metrics: SimulationMetrics | null;
}

const TrendCharts: React.FC<Props> = ({ metrics }) => {
  if (!metrics) return <div>No metrics available</div>;

  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', marginTop: '1rem' }}>
      <h3>Current Metrics (Snapshot)</h3>
      {/*
        In a real app, this would use Recharts to plot history.
        Here we just show the latest snapshot values.
      */}
      <ul>
        <li>MCS Step: {metrics.mcs}</li>
        <li>Density: {(metrics.density * 100).toFixed(2)}%</li>
        <li>Porosity: {(metrics.porosity * 100).toFixed(2)}%</li>
        <li>Avg Grain Radius: {metrics.corrected_radius.toFixed(4)}</li>
        <li>Number of Clusters: {metrics.num_clusters}</li>
      </ul>
    </div>
  );
};

export default TrendCharts;
