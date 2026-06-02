import pytest
import numpy as np
from model_lab import _nice_step, _place_on_ground


def test_nice_step_small():
    assert _nice_step(8) == 1

def test_nice_step_medium():
    assert _nice_step(80) == 10

def test_nice_step_large():
    assert _nice_step(800) == 100

def test_nice_step_mid_range():
    assert _nice_step(40) == 5

def test_nice_step_two_range():
    assert _nice_step(16) == 2

def test_place_on_ground_bottom_at_z0():
    import trimesh
    mesh = trimesh.creation.box(extents=[10, 10, 10])
    mesh.apply_translation([50, 30, 20])
    _place_on_ground(mesh)
    assert np.isclose(mesh.bounds[0][2], 0.0, atol=1e-6)

def test_place_on_ground_xy_centered():
    import trimesh
    mesh = trimesh.creation.box(extents=[10, 20, 5])
    mesh.apply_translation([100, 200, 300])
    _place_on_ground(mesh)
    center = (mesh.bounds[0] + mesh.bounds[1]) / 2
    assert np.isclose(center[0], 0.0, atol=1e-6)
    assert np.isclose(center[1], 0.0, atol=1e-6)

def test_place_on_ground_preserves_shape():
    import trimesh
    mesh = trimesh.creation.box(extents=[10, 20, 5])
    mesh.apply_translation([100, 200, 300])
    original_extents = mesh.bounds[1] - mesh.bounds[0]
    _place_on_ground(mesh)
    assert np.allclose(mesh.bounds[1] - mesh.bounds[0], original_extents, atol=1e-6)
