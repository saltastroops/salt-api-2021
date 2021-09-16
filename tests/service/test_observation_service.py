from typing import cast, List, Dict, Any

import pytest

from saltapi.exceptions import NotFoundError
from saltapi.repository.block_repository import BlockRepository
from saltapi.service.observations_service import ObservationService


class FakeBlockRepository:
    def __init__(self) -> None:
        self.block_visit_status = "In queue"

    def get_observations(self, block_visit_id: int) -> List[Dict[str, Any]]:
        if block_visit_id == BLOCK_VISIT_ID:
            observations = [
                {
                    "observation_time": 2466,
                    "overhead_time": 0,
                    "target": {
                        "id": 1,
                        "name": "H1000-000",
                        "coordinates": {
                            "right_ascension": 201.73749999999998,
                            "declination": -30.72833333333333,
                            "equinox": 2000.0
                        },
                        "proper_motion": None,
                        "magnitude": {
                            "minimum_magnitude": 13.0,
                            "maximum_magnitude": 25.0,
                            "bandpass": "V"
                        },
                        "target_type": "Galaxies - elliptical galaxy",
                        "period_ephemeris": None,
                        "horizons_identifier": None
                    },
                    "finder_charts": [
                        {
                            "id": 1303,
                            "comment": None,
                            "valid_from": None,
                            "valid_until": None
                        }
                    ],
                    "time_restrictions": None,
                    "phase_constraints": None,
                    "telescope_configurations": [
                        {
                            "iterations": 1,
                            "position_angle": 0.0,
                            "use_parallactic_angle": False,
                            "dither_pattern": None,
                            "guide_star": None,
                            "payload_configurations": [
                                {
                                    "payload_configuration_type": None,
                                    "use_calibration_screen": False,
                                    "lamp": None,
                                    "calibration_filter": "None",
                                    "guide_method": "None",
                                    "instruments":
                                        {
                                            "salticam": [
                                                {
                                                    "id": 2,
                                                    "detector":
                                                        {
                                                            "mode": "Normal",
                                                            "pre_binned_rows": 2,
                                                            "pre_binned_columns": 2,
                                                            "iterations": 1,
                                                            "exposure_type": "Science",
                                                            "gain": "Faint",
                                                            "readout_speed": "Slow",
                                                            "detector_windows": None
                                                        },
                                                    "procedure": {
                                                        "cycles": 2,
                                                        "exposures": [
                                                            {
                                                                "filter": {
                                                                    "name": "B-S1",
                                                                    "description": "Johnson B"
                                                                },
                                                                "exposure_time": 6.0
                                                            },
                                                            {
                                                                "filter": {
                                                                    "name": "V-S1",
                                                                    "description": "Johnson V"
                                                                },
                                                                "exposure_time": 18.0
                                                            }
                                                        ]},
                                                    "minimum_signal_to_noise": 0,
                                                    "observation_time": 500.3,
                                                    "overhead_time": 0.0
                                                }
                                            ],
                                            "rss": None,
                                            "hrs": None,
                                            "bvit": None
                                        }
                                }
                            ]
                        }
                    ]
                }
            ]
            return observations
        raise NotFoundError

    def get_observations_status(self, block_visit_id: int) -> str:
        if block_visit_id == BLOCK_VISIT_ID:
            return self.block_visit_status
        raise NotFoundError()

    def update_observations_status(
            self, block_id: int, value: str
    ) -> None:
        if block_id == BLOCK_VISIT_ID:
            self.block_visit_status = value
        else:
            raise NotFoundError()


OBSERVATION = [
    {
        "observation_time": 2466,
        "overhead_time": 0,
        "target": {
            "id": 1,
            "name": "H1000-000",
            "coordinates": {
                "right_ascension": 201.73749999999998,
                "declination": -30.72833333333333,
                "equinox": 2000.0
            },
            "proper_motion": None,
            "magnitude": {
                "minimum_magnitude": 13.0,
                "maximum_magnitude": 25.0,
                "bandpass": "V"
            },
            "target_type": "Galaxies - elliptical galaxy",
            "period_ephemeris": None,
            "horizons_identifier": None
        },
        "finder_charts": [
            {
                "id": 1303,
                "comment": None,
                "valid_from": None,
                "valid_until": None
            }
        ],
        "time_restrictions": None,
        "phase_constraints": None,
        "telescope_configurations": [
            {
                "iterations": 1,
                "position_angle": 0.0,
                "use_parallactic_angle": False,
                "dither_pattern": None,
                "guide_star": None,
                "payload_configurations": [
                    {
                        "payload_configuration_type": None,
                        "use_calibration_screen": False,
                        "lamp": None,
                        "calibration_filter": "None",
                        "guide_method": "None",
                        "instruments":
                            {
                                "salticam": [
                                    {
                                        "id": 2,
                                        "detector":
                                            {
                                                "mode": "Normal",
                                                "pre_binned_rows": 2,
                                                "pre_binned_columns": 2,
                                                "iterations": 1,
                                                "exposure_type": "Science",
                                                "gain": "Faint",
                                                "readout_speed": "Slow",
                                                "detector_windows": None
                                            },
                                        "procedure": {
                                            "cycles": 2,
                                            "exposures": [
                                                {
                                                    "filter": {
                                                        "name": "B-S1",
                                                        "description": "Johnson B"
                                                    },
                                                    "exposure_time": 6.0
                                                },
                                                {
                                                    "filter": {
                                                        "name": "V-S1",
                                                        "description": "Johnson V"
                                                    },
                                                    "exposure_time": 18.0
                                                }
                                            ]},
                                        "minimum_signal_to_noise": 0,
                                        "observation_time": 500.3,
                                        "overhead_time": 0.0
                                    }
                                ],
                                "rss": None,
                                "hrs": None,
                                "bvit": None
                            }
                    }
                ]
            }
        ]
    }
]


BLOCK_VISIT_ID = 1


def create_observations_service() -> ObservationService:
    block_repository = cast(BlockRepository, FakeBlockRepository())
    return ObservationService(block_repository)


def test_get_observations() -> None:
    observations_service = create_observations_service()
    observation = observations_service.get_observations(BLOCK_VISIT_ID)

    assert OBSERVATION == observation


def test_get_observations_status_raises_error_for_wrong_block_id() -> None:
    observations_service = create_observations_service()
    with pytest.raises(NotFoundError):
        observations_service.get_observations_status(1234567)


def test_get_observations_status() -> None:
    observations_service = create_observations_service()
    status = observations_service.get_observations_status(BLOCK_VISIT_ID)
    assert status == "In queue"


def test_update_observations_status() -> None:
    observations_service = create_observations_service()

    old_status = observations_service.get_observations_status(BLOCK_VISIT_ID)
    assert old_status != "Accepted"

    observations_service.update_observations_status(BLOCK_VISIT_ID, "Accepted")

    new_status = observations_service.get_observations_status(BLOCK_VISIT_ID)
    assert new_status == "Accepted"


def test_update_observations_status_raises_error_for_wrong_block_id() -> None:
    observations_service = create_observations_service()
    with pytest.raises(NotFoundError):
        observations_service.update_observations_status(0, "In queue")
