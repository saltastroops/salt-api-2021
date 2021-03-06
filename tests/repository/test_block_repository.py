from typing import Any, Callable, cast

import pytest
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound

from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.service.instrument import BVIT, HRS, RSS, Salticam
from saltapi.service.target import Target
from tests.markers import nodatabase

TEST_DATA = "repository/block_repository.yaml"


class FakeTargetRepository:
    def get(self, target_id: int) -> Target:
        return f"Target with id {target_id}"


class FakeInstrumentRepository:
    def get_salticam(self, salticam_id: int) -> Salticam:
        return f"Salticam with id {salticam_id}"

    def get_rss(self, rss_id: int) -> RSS:
        return f"RSS with id {rss_id}"

    def get_hrs(self, hrs_id: int) -> HRS:
        return f"HRS with id {hrs_id}"

    def get_bvit(self, bvit_id: int) -> BVIT:
        return f"BVIT with id {bvit_id}"


def create_block_repository(connection: Connection) -> BlockRepository:
    return BlockRepository(
        target_repository=cast(TargetRepository, FakeTargetRepository()),
        instrument_repository=cast(InstrumentRepository, FakeInstrumentRepository()),
        connection=connection,
    )


@nodatabase
def test_get_block_returns_block_content(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["general_block_details"]
    block_id = data["id"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)

    for key in data:
        assert key in block
        assert block[key] == data[key]


@nodatabase
def test_get_raises_error_for_too_complicated_blocks(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    # Blocks with multiple observations or with subblocks or subsubblocks should cause
    # an error

    data = testdata(TEST_DATA)["too_complicated_blocks"]
    block_ids = data["block_ids"]
    block_repository = create_block_repository(dbconnection)
    for block_id in block_ids:
        with pytest.raises(ValueError) as excinfo:
            block_repository.get(block_id)
        assert "supported" in str(excinfo)


@nodatabase
def test_get_returns_executed_observations(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["executed_observations"]
    block_id = data["block_id"]
    expected_observations = data["observations"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    observations = block["executed_observations"]

    assert len(observations) == len(expected_observations)
    for i in range(len(observations)):
        assert observations[i] == expected_observations[i]


@nodatabase
def test_get_returns_observing_windows(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["observing_windows"]
    block_id = data["block_id"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    observing_windows = block["observing_windows"]

    assert len(observing_windows) == data["window_count"]
    assert observing_windows[0] == data["first_window"]
    assert observing_windows[-1] == data["last_window"]
    for i in range(len(observing_windows) - 1):
        # the windows are sorted
        assert observing_windows[i]["start"] < observing_windows[i + 1]["start"]


@nodatabase
def test_target(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["target"]
    block_id = data["block_id"]
    expected_target_id = data["target_id"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    target = block["observations"][0]["target"]

    assert target == f"Target with id {expected_target_id}"


@nodatabase
def test_finder_charts(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["finder_charts"]
    for d in data:
        block_id = d["block_id"]
        expected_finder_charts = d["finder_charts"]
        block_repository = create_block_repository(dbconnection)
        block = block_repository.get(block_id)
        finder_charts = block["observations"][0]["finder_charts"]

        assert finder_charts == expected_finder_charts


@nodatabase
def test_finder_charts_with_validity(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["finder_charts_with_validity"]
    block_id = data["block_id"]
    expected_last_finder_chart = data["last_finder_chart"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    finder_charts = block["observations"][0]["finder_charts"]

    assert finder_charts[-1] == expected_last_finder_chart


@nodatabase
def test_time_restrictions(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["time_restrictions"]
    block_id = data["block_id"]
    expected_restrictions = data["restrictions"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    restrictions = block["observations"][0]["time_restrictions"]

    assert len(restrictions) == len(expected_restrictions)
    for i in range(len(restrictions)):
        assert restrictions[i]["end"] == expected_restrictions[i]["end"]


@nodatabase
def test_no_time_restrictions(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["no_time_restrictions"]
    block_id = data["block_id"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    restrictions = block["observations"][0]["time_restrictions"]

    assert restrictions is None


@nodatabase
def test_phase_constraints(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["phase_constraints"]
    block_id = data["block_id"]
    expected_constraints = data["constraints"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    constraints = block["observations"][0]["phase_constraints"]

    assert constraints == expected_constraints


@nodatabase
def test_no_phase_constraints(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["no_phase_constraints"]
    block_id = data["block_id"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    constraints = block["observations"][0]["phase_constraints"]

    assert constraints is None


@nodatabase
def test_telescope_configuration(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["telescope_configurations"]
    for d in data:
        block_id = d["block_id"]
        expected_telescope_config = d["telescope_config"]
        block_repository = create_block_repository(dbconnection)
        block = block_repository.get(block_id)
        telescope_config = block["observations"][0]["telescope_configurations"][0]

        for key in expected_telescope_config:
            assert key in telescope_config
            assert telescope_config[key] == expected_telescope_config[key]


@nodatabase
def test_dither_pattern(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["dither_pattern"]
    block_id = data["block_id"]
    expected_telescope_configs = data["telescope_configs"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    telescope_configs = block["observations"][0]["telescope_configurations"]

    assert len(telescope_configs) == len(expected_telescope_configs)
    for i in range(len(telescope_configs)):
        assert (
            telescope_configs[i]["dither_pattern"]
            == expected_telescope_configs[i]["dither_pattern"]
        )


@nodatabase
def test_guide_star(dbconnection: Connection, testdata: Callable[[str], Any]) -> None:
    data = testdata(TEST_DATA)["guide_star"]
    for d in data:
        block_id = d["block_id"]
        expected_guide_star = d["star"]
        block_repository = create_block_repository(dbconnection)
        block = block_repository.get(block_id)
        guide_star = block["observations"][0]["telescope_configurations"][0][
            "guide_star"
        ]
        assert pytest.approx(guide_star["right_ascension"]) == pytest.approx(
            expected_guide_star["right_ascension"]
        )
        assert pytest.approx(
            guide_star["declination"]
            == pytest.approx(expected_guide_star["declination"])
        )
        assert guide_star["equinox"] == expected_guide_star["equinox"]
        assert guide_star["magnitude"] == expected_guide_star["magnitude"]


def test_no_guide_star(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["no_guide_star"]
    block_id = data["block_id"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    guide_star = block["observations"][0]["telescope_configurations"][0]["guide_star"]
    assert guide_star is None


@nodatabase
def test_get_raises_error_for_non_existing_block(dbconnection: Connection) -> None:
    block_repository = create_block_repository(dbconnection)
    with pytest.raises(NoResultFound):
        block_repository.get(1234567)


@nodatabase
def test_payload_configurations(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["payload_configurations"]
    block_id = data["block_id"]
    expected_configs = data["configurations"]
    block_repository = create_block_repository(dbconnection)
    block = block_repository.get(block_id)
    configs = block["observations"][0]["telescope_configurations"][0][
        "payload_configurations"
    ]

    assert len(configs) == len(expected_configs)

    for i in range(len(configs)):
        # instruments must be compared separately
        instruments = set(configs[i]["instruments"].keys()).union(
            expected_configs[i]["instruments"].keys()
        )
        for instrument in instruments:
            assert configs[i]["instruments"].get(instrument) == expected_configs[i][
                "instruments"
            ].get(instrument)
        del configs[i]["instruments"]
        del expected_configs[i]["instruments"]

        assert configs[i] == expected_configs[i]


def test_get_block_instruments(
    dbconnection: Connection, testdata: Callable[[str], Any]
) -> None:
    data = testdata(TEST_DATA)["block_instruments"]
    for d in data:
        block_id = d["block_id"]
        expected_observations = d["observations"]
        block_repository = create_block_repository(dbconnection)
        block = block_repository.get(block_id)
        observations = block["observations"]

        assert len(observations) == len(expected_observations)
        for i in range(len(observations)):
            expected_telescope_configs = expected_observations[i][
                "telescope_configurations"
            ]
            telescope_configs = observations[i]["telescope_configurations"]

            assert len(expected_telescope_configs) == len(telescope_configs)
            for j in range(len(telescope_configs)):
                expected_payload_configs = expected_telescope_configs[j][
                    "payload_configurations"
                ]
                payload_configs = telescope_configs[j]["payload_configurations"]

                assert len(payload_configs) == len(expected_payload_configs)

                for k in range(len(payload_configs)):
                    instruments = set(payload_configs[k]["instruments"].keys()).union(
                        expected_payload_configs[k]["instruments"].keys()
                    )
                    for instrument in instruments:
                        assert payload_configs[k]["instruments"].get(
                            instrument
                        ) == expected_payload_configs[k]["instruments"].get(instrument)
