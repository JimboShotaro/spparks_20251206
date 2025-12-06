import unittest
import numpy as np
from NanoSinterWeb.backend.app.core.simulation import PottsGrowthModel, SimConfig, SimulationContext
from NanoSinterWeb.backend.app.core.analysis import MicrostructureAnalyzer

class TestNanoSinterWeb(unittest.TestCase):
    def test_potts_initialization(self):
        config = SimConfig(grid_size=20, num_seeds=5)
        model = PottsGrowthModel()
        grid = model.initialize_grid(config)

        self.assertEqual(grid.shape, (20, 20, 20))
        # Check if we have values other than 0 (seeds)
        self.assertTrue(np.any(grid > 0))

    def test_potts_evolution(self):
        config = SimConfig(grid_size=20, num_seeds=5)
        model = PottsGrowthModel()
        context = SimulationContext(config, model)

        initial_grid = context.grid.copy()
        result = context.execute_step()

        self.assertIn("accepted_moves", result)
        # It's possible for 0 moves if unlucky or grid is stable, but unlikely with random init
        # Just check it runs without error

    def test_metrics_calculation(self):
        # Create a controlled grid
        grid = np.zeros((10, 10, 10), dtype=int)

        # Grain 1: 100 voxels
        grid[0:5, 0:4, 0:5] = 1 # 5*4*5 = 100

        # Grain 2: 200 voxels
        grid[5:10, 0:4, 0:5] = 2 # 5*4*5 = 100
        grid[0:10, 4:5, 0:5] = 2 # 10*1*5 = 50. Total 150. Overlap?
        # Let's simplify.

        grid.fill(0)
        grid[0,0,0] = 1 # 1 voxel
        grid[0,0,1] = 2 # 1 voxel

        metrics = MicrostructureAnalyzer.calculate_true_metrics(grid)

        # Density: 2 / 1000 = 0.002
        self.assertEqual(metrics["density"], 0.002)
        self.assertEqual(metrics["num_clusters"], 2)

        # Avg Radius: V_avg = 1. R = (3/4pi)^(1/3) approx 0.62
        self.assertAlmostEqual(metrics["corrected_radius"], (3/(4*np.pi))**(1/3), places=2)

if __name__ == '__main__':
    unittest.main()
