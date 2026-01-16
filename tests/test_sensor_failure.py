import numpy as np
from src.utils.sensor_outliers_detection import SensorDataHandler
from config import settings as set

def test_no_measurement():
    """Tests the detect_abnormanl_state for no measurements"""
    sensor_handler = SensorDataHandler()
    report = sensor_handler.get_abnormal_state_report_message(None, None)
    assert report == set.NO_MEASUREMENT_MSG
    report = sensor_handler.get_abnormal_state_report_message(set.HIGH_HUMIDITY_THRESHOLD -1, set.HIGH_TEMPERATURE_THRESHOLD - 1)
    assert report != set.NO_MEASUREMENT_MSG
    report = sensor_handler.get_abnormal_state_report_message(set.HIGH_HUMIDITY_THRESHOLD + 1, set.HIGH_TEMPERATURE_THRESHOLD + 1)
    assert report != set.NO_MEASUREMENT_MSG

def test_outlier_value_detection():
    """Tests the detect_abnormanl_state for no measurements"""
    sensor_handler = SensorDataHandler()

    # Test with No measurement values
    report = sensor_handler.get_abnormal_state_report_message(None, None)
    assert report != set.OUTLIER_DETECTED_MSG

    # Test with valid values
    report = sensor_handler.get_abnormal_state_report_message(set.HIGH_HUMIDITY_THRESHOLD -1, set.HIGH_TEMPERATURE_THRESHOLD - 1)
    assert report != set.OUTLIER_DETECTED_MSG

    # Tests with thresholds ouliers values
    report = sensor_handler.get_abnormal_state_report_message(set.HIGH_HUMIDITY_THRESHOLD + 1, set.HIGH_TEMPERATURE_THRESHOLD + 1)
    assert report == set.OUTLIER_DETECTED_MSG

def test_normal_state():
    """Tests the detect_abnormanl_state for no measurements"""
    sensor_handler = SensorDataHandler()

    # Test with No measurement values
    report = sensor_handler.get_abnormal_state_report_message(None, None)
    assert report != set.SENSOR_OK_MSG

    # Test with valid values
    report = sensor_handler.get_abnormal_state_report_message(set.HIGH_HUMIDITY_THRESHOLD -1, set.HIGH_TEMPERATURE_THRESHOLD - 1)
    assert report == set.SENSOR_OK_MSG

    # Tests with thresholds ouliers values
    report = sensor_handler.get_abnormal_state_report_message(set.HIGH_HUMIDITY_THRESHOLD + 1, set.HIGH_TEMPERATURE_THRESHOLD + 1)
    assert report != set.SENSOR_OK_MSG




