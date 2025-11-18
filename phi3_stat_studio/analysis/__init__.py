"""Statistical analysis modules."""

from .descriptive import compute_descriptive_statistics
from .t_tests import one_sample_t_test, independent_t_test
from .plots import create_histogram, create_scatter_plot

__all__ = [
    "compute_descriptive_statistics",
    "one_sample_t_test",
    "independent_t_test",
    "create_histogram",
    "create_scatter_plot",
]


