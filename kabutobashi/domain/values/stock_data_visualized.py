from dataclasses import dataclass

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class StockDataVisualized:
    """
    StockDataVisualized: ValueObject
    Used to visualize.
    """

    fig: plt.Figure
    size_ratio: int
