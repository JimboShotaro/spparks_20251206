import React, { useState } from 'react';
import { SimConfig } from '../types';

interface Props {
  onSubmit: (config: SimConfig) => void;
}

const SimulationConfigForm: React.FC<Props> = ({ onSubmit }) => {
  const [config, setConfig] = useState<SimConfig>({
    gridSize: 50,
    temperature: 1.0,
    initialPorosity: 0.3,
    eventRatios: {
      growth: 2.0,
      migration: 1.0,
      annihilation: 4.0
    },
    numSeeds: 20
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };

  const handleRatioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      eventRatios: {
        ...prev.eventRatios,
        [name]: parseFloat(value)
      }
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(config);
  };

  return (
    <form onSubmit={handleSubmit} style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '4px' }}>
      <h3>Simulation Configuration</h3>
      <div>
        <label>Grid Size:</label>
        <input type="number" name="gridSize" value={config.gridSize} onChange={handleChange} />
      </div>
      <div>
        <label>Temperature (kT):</label>
        <input type="number" step="0.1" name="temperature" value={config.temperature} onChange={handleChange} />
      </div>
      <div>
        <label>Initial Porosity:</label>
        <input type="number" step="0.01" max="1" min="0" name="initialPorosity" value={config.initialPorosity} onChange={handleChange} />
      </div>
      <div>
        <label>Number of Seeds:</label>
        <input type="number" name="numSeeds" value={config.numSeeds} onChange={handleChange} />
      </div>

      <h4>Event Ratios</h4>
      <div>
        <label>Growth:</label>
        <input type="number" step="0.1" name="growth" value={config.eventRatios.growth} onChange={handleRatioChange} />
      </div>
      <div>
        <label>Migration:</label>
        <input type="number" step="0.1" name="migration" value={config.eventRatios.migration} onChange={handleRatioChange} />
      </div>
      <div>
        <label>Annihilation:</label>
        <input type="number" step="0.1" name="annihilation" value={config.eventRatios.annihilation} onChange={handleRatioChange} />
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
        <button type="button" onClick={() => onPreview(config)}>Generate Preview</button>
        <button type="submit">Start Simulation</button>
      </div>
    </form>
  );
};

export default SimulationConfigForm;
