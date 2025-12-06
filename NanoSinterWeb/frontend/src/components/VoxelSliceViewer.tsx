import React, { useEffect, useRef, useState } from 'react';
import { VoxelData } from '../types';

interface Props {
  jobId: string;
  gridSize: number;
}

const VoxelSliceViewer: React.FC<Props> = ({ jobId, gridSize }) => {
  const [z, setZ] = useState(Math.floor(gridSize / 2));
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!jobId) return;

    // Fetch slice data
    fetch(`http://localhost:8000/api/jobs/${jobId}/slice/${z}`)
      .then(res => res.json())
      .then((data: VoxelData) => {
        drawSlice(data);
      })
      .catch(err => console.error("Error fetching slice:", err));
  }, [jobId, z]);

  const drawSlice = (voxelData: VoxelData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const [width, height] = voxelData.dims;
    // Assume square canvas for now
    const scale = canvas.width / width;

    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < width; i++) {
      for (let j = 0; j < height; j++) {
        const val = voxelData.data[i * height + j];
        if (val === 0) {
          ctx.fillStyle = '#000000'; // Pore
        } else if (val === -1) {
          ctx.fillStyle = '#0000FF'; // Boundary
        } else {
          // Hash ID to color
          const hue = (val * 137.508) % 360;
          ctx.fillStyle = `hsl(${hue}, 50%, 50%)`;
        }
        ctx.fillRect(i * scale, j * scale, scale, scale);
      }
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', marginTop: '1rem' }}>
      <h3>Voxel Slice Viewer</h3>
      <div>
        <label>Z-Slice: {z}</label>
        <input
          type="range"
          min="0"
          max={gridSize - 1}
          value={z}
          onChange={e => setZ(parseInt(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>
      <canvas
        ref={canvasRef}
        width={300}
        height={300}
        style={{ border: '1px solid #000' }}
      />
    </div>
  );
};

export default VoxelSliceViewer;
