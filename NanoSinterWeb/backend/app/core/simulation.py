from abc import ABC, abstractmethod
import numpy as np
import random
from ..models import SimConfig

class ModelStrategy(ABC):
    """Abstract base class for KMC algorithms"""

    @abstractmethod
    def initialize_grid(self, config: SimConfig) -> np.ndarray:
        pass

    @abstractmethod
    def evolve(self, grid: np.ndarray, temp: float) -> dict:
        """Execute 1 Monte Carlo Step (MCS) and return statistics"""
        pass

class PottsGrowthModel(ModelStrategy):
    def initialize_grid(self, config: SimConfig) -> np.ndarray:
        size = config.grid_size
        grid = np.zeros((size, size, size), dtype=int)

        # Place seeds (Phase 1)
        if config.num_seeds:
            for i in range(1, config.num_seeds + 1):
                while True:
                    rx = random.randint(0, size - 1)
                    ry = random.randint(0, size - 1)
                    rz = random.randint(0, size - 1)
                    if grid[rx, ry, rz] == 0:
                        grid[rx, ry, rz] = i
                        break

        # Grow to fill space (Phase 2: Grain Growth)
        # This mocks the "SPPARKS run" to fill the volume from seeds
        # We perform iterative growth until no empty spots remain

        # To make it efficient for prototype:
        # Identify empty spots and fill them with nearest neighbor logic (Voronoi approx)
        # Or run the evolve logic until full.

        # Simple Voronoi-like filling:
        # For every empty cell, assign the value of the nearest seed.
        # This is slow O(N^3 * Seeds).

        # Alternative: Breadth-First Search (Flood Fill) from all seeds simultaneously.
        from collections import deque
        queue = deque()

        # Add all seeds to queue
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if grid[x, y, z] != 0:
                        queue.append((x, y, z))

        # Directions
        dirs = [
            (1,0,0), (-1,0,0),
            (0,1,0), (0,-1,0),
            (0,0,1), (0,0,-1)
        ]

        while queue:
            cx, cy, cz = queue.popleft()
            val = grid[cx, cy, cz]

            # Shuffle directions for randomness to avoid square grains
            random.shuffle(dirs)

            for dx, dy, dz in dirs:
                nx, ny, nz = (cx + dx) % size, (cy + dy) % size, (cz + dz) % size
                if grid[nx, ny, nz] == 0:
                    grid[nx, ny, nz] = val
                    queue.append((nx, ny, nz))

        # All filled
        return grid

    def evolve(self, grid: np.ndarray, temp: float) -> dict:
        # Simplified Glauber dynamics simulation
        changes = 0
        size = grid.shape[0]
        num_attempts = size * size * size // 10 # 0.1 MCS

        # Vectorized attempt for prototype speed (though logic is approximated)
        x = np.random.randint(0, size, num_attempts)
        y = np.random.randint(0, size, num_attempts)
        z = np.random.randint(0, size, num_attempts)

        # Get neighbors (randomly one of 6 neighbors)
        # direction: 0:x+, 1:x-, 2:y+, 3:y-, 4:z+, 5:z-
        direction = np.random.randint(0, 6, num_attempts)

        dx = np.zeros(num_attempts, dtype=int)
        dy = np.zeros(num_attempts, dtype=int)
        dz = np.zeros(num_attempts, dtype=int)

        dx[direction == 0] = 1
        dx[direction == 1] = -1
        dy[direction == 2] = 1
        dy[direction == 3] = -1
        dz[direction == 4] = 1
        dz[direction == 5] = -1

        nx = (x + dx) % size
        ny = (y + dy) % size
        nz = (z + dz) % size

        current_vals = grid[x, y, z]
        neighbor_vals = grid[nx, ny, nz]

        mask = current_vals != neighbor_vals
        # Accept move (simplified)
        grid[x[mask], y[mask], z[mask]] = neighbor_vals[mask]

        changes = np.sum(mask)

        return {"accepted_moves": int(changes)}

class SGGSSinteringStrategy(ModelStrategy):
    """Sandia Grain Growth & Sintering model implementation"""
    def __init__(self, ratios: dict):
        self.ratios = ratios
        self.growth_model = PottsGrowthModel() # Use growth model for initialization

    def initialize_grid(self, config: SimConfig) -> np.ndarray:
        # Step 1 & 2: Generate Polycrystal using Potts Growth
        grid = self.growth_model.initialize_grid(config)

        # Step 3: Apply Porosity
        # Randomly turn sites to 0
        total_sites = grid.size
        num_pores = int(total_sites * config.initial_porosity)

        # Using indices for speed
        flat = grid.flatten()
        indices = np.random.choice(total_sites, num_pores, replace=False)
        flat[indices] = 0

        grid = flat.reshape(grid.shape)

        return grid

    def evolve(self, grid: np.ndarray, temp: float) -> dict:
        # Placeholder for sintering logic: pore migration and annihilation
        size = grid.shape[0]
        num_attempts = size * size * size // 10

        # Logic would go here

        changes = 0
        return {"accepted": int(changes)}

class SimulationContext:
    def __init__(self, config: SimConfig, strategy: ModelStrategy):
        self.config = config
        self.strategy = strategy
        self.grid = self.strategy.initialize_grid(config)
        self.step = 0

    def execute_step(self):
        self.step += 1
        return self.strategy.evolve(self.grid, self.config.temperature)

    def save_snapshot(self, path: str):
        np.save(path, self.grid)
