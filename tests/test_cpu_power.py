"""
Tests the module 'cpu_power.py'.
"""

from src.models.cpu import CPU
from src.config.settings import CPUPowerSettings as cp

def test_status_report_high():
    """Tests the status report for high threshold."""
    cpu = CPU()

    cpu.temperature = cp.HIG_THRESHOLD + 1
    report = cpu.status_report()
    assert report == cp.HIGTHR_MSG

    cpu.temperature = cp.HIG_THRESHOLD
    report = cpu.status_report()
    assert report == cp.HIGTHR_MSG

    cpu.temperature = cp.HIG_THRESHOLD - 1
    report = cpu.status_report()
    assert report != cp.HIGTHR_MSG


def test_status_report_low():
    """Tests the status report for low threshold."""
    cpu = CPU()

    cpu.temperature = cp.LOW_THRESHOLD + 1
    report = cpu.status_report()
    assert report == cp.LOWTHR_MSG

    cpu.temperature = cp.LOW_THRESHOLD
    report = cpu.status_report()
    assert report == cp.LOWTHR_MSG

    cpu.temperature = cp.LOW_THRESHOLD - 1
    report = cpu.status_report()
    assert report != cp.LOWTHR_MSG


def test_status_report_normal():
    """Tests the status report for normal operation."""
    cpu = CPU()

    cpu.temperature = cp.LOW_THRESHOLD - 1
    report = cpu.status_report()
    assert report == cp.NORMAL_MSG

    cpu.temperature = cp.LOW_THRESHOLD
    report = cpu.status_report()
    assert report != cp.NORMAL_MSG

    cpu.temperature = cp.LOW_THRESHOLD + 1
    report = cpu.status_report()
    assert report != cp.NORMAL_MSG
    
