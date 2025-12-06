import numpy as np

class MicrostructureAnalyzer:
    """Class to perform accurate grain size calculation as per thesis"""

    @staticmethod
    def calculate_true_metrics(grid: np.ndarray) -> dict:
        """
        Calculate statistics excluding pores (0) and boundaries (-1).
        """
        valid_grain_mask = (grid != 0) & (grid != -1)

        solid_volume = np.sum(valid_grain_mask)
        total_volume = grid.size
        density = solid_volume / total_volume if total_volume > 0 else 0.0

        porosity = 1.0 - density

        # Simple grain count approximation
        unique_ids = np.unique(grid[valid_grain_mask])
        num_clusters = len(unique_ids)

        # Approximate average radius assuming spherical grains: V = 4/3 * pi * r^3
        # V_avg = solid_volume / num_clusters
        if num_clusters > 0:
            avg_volume = solid_volume / num_clusters
            avg_radius = (avg_volume * 3 / (4 * np.pi))**(1/3)
        else:
            avg_radius = 0.0

        return {
            "density": float(density),
            "corrected_radius": float(avg_radius),
            "porosity": float(porosity),
            "num_clusters": int(num_clusters)
        }
