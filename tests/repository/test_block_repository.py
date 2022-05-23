from typing import Callable, cast

import pytest
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoResultFound

from saltapi.exceptions import NotFoundError
from saltapi.repository.block_repository import BlockRepository
from saltapi.repository.instrument_repository import InstrumentRepository
from saltapi.repository.target_repository import TargetRepository
from saltapi.service.instrument import BVIT, HRS, RSS, Salticam
from saltapi.service.target import Target
from saltapi.web.schema.block import Block as _Block
from tests.markers import nodatabase


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
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 79390
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    block["observing_conditions"]["maximum_lunar_phase"] = float(
        block["observing_conditions"]["maximum_lunar_phase"]
    )
    block["observing_conditions"]["minimum_lunar_distance"] = float(
        block["observing_conditions"]["minimum_lunar_distance"]
    )
    check_block(block)


@nodatabase
@pytest.mark.parametrize("block_id", [9005, 9495])
def test_get_raises_error_for_too_complicated_blocks(
    block_id: int, db_connection: Connection
) -> None:
    # Blocks with multiple observations or with subblocks or subsubblocks should cause
    # an error
    block_repository = create_block_repository(db_connection)
    with pytest.raises(ValueError) as excinfo:
        block_repository.get(block_id)
        assert "supported" in str(excinfo)


@nodatabase
def test_get_returns_block_visits(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 79390
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert "block_visits" in block
    check_block(block)


@nodatabase
def test_get_returns_observing_windows(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(89175)

    assert "observing_windows" in block
    assert "start" in block["observing_windows"][0]
    assert "end" in block["observing_windows"][0]

    for i in range(len(block["observing_windows"]) - 1):
        # the windows are sorted
        assert (
            block["observing_windows"][i]["start"]
            < block["observing_windows"][i + 1]["start"]
        )
    check_block(block)


@nodatabase
def test_target(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(88649)
    print(block)
    assert "target" in block["observations"][0]
    check_block(block)


@nodatabase
@pytest.mark.parametrize("block_id", [75444, 75551])
def test_finder_charts(
    block_id: int, db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert "finder_charts" in block["observations"][0]
    check_block(block)


@nodatabase
def test_finder_charts_with_validity(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(87431)
    finder_charts = block["observations"][0]["finder_charts"]

    assert "valid_from" in finder_charts[0]
    assert "valid_until" in finder_charts[0]
    check_block(block)


@nodatabase
def test_time_restrictions(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 88042
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert "time_restrictions" in block["observations"][0]

    assert "start" in block["observations"][0]["time_restrictions"][0]
    assert "end" in block["observations"][0]["time_restrictions"][0]
    check_block(block)


@nodatabase
def test_no_time_restrictions(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 89403
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    restrictions = block["observations"][0]["time_restrictions"]

    assert restrictions is None
    check_block(block)


@nodatabase
def test_phase_constraints(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 69787
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert "phase_constraints" in block["observations"][0]

    assert "start" in block["observations"][0]["phase_constraints"][0]
    assert "end" in block["observations"][0]["phase_constraints"][0]
    check_block(block)


@nodatabase
def test_no_phase_constraints(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 89403
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    constraints = block["observations"][0]["phase_constraints"]

    assert constraints is None
    check_block(block)


@nodatabase
@pytest.mark.parametrize("block_id", [89463, 89382])
def test_telescope_configuration(
    block_id: int, db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert "telescope_configurations" in block["observations"][0]
    expected_telescope_config = block["observations"][0]["telescope_configurations"][0]

    assert "iterations" in expected_telescope_config
    assert "position_angle" in expected_telescope_config
    assert "use_parallactic_angle" in expected_telescope_config
    check_block(block)


@nodatabase
def test_dither_pattern(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 89445
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    telescope_configs = block["observations"][0]["telescope_configurations"]

    for config in telescope_configs:
        assert "dither_pattern" in config
    check_block(block)


@nodatabase
@pytest.mark.parametrize("block_id", [89204, 84611])
def test_guide_star(
    block_id: int, db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert "guide_star" in block["observations"][0]["telescope_configurations"][0]
    guide_star = block["observations"][0]["telescope_configurations"][0]["guide_star"]

    assert "right_ascension" in guide_star
    assert "declination" in guide_star
    assert "equinox" in guide_star
    assert "magnitude" in guide_star
    check_block(block)


@nodatabase
def test_no_guide_star(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 89480
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    guide_star = block["observations"][0]["telescope_configurations"][0]["guide_star"]
    assert guide_star is None
    check_block(block)


@nodatabase
def test_get_raises_error_for_non_existing_block(db_connection: Connection) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NoResultFound):
        block_repository.get(1234567)


@nodatabase
def test_payload_configurations(
    db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_id = 89326
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    assert (
        "payload_configurations"
        in block["observations"][0]["telescope_configurations"][0]
    )
    payload_config = block["observations"][0]["telescope_configurations"][0][
        "payload_configurations"
    ][0]

    assert "instruments" in payload_config
    assert "guide_method" in payload_config
    assert "payload_configuration_type" in payload_config
    check_block(block)


@nodatabase
@pytest.mark.parametrize("block_id", [89444, 76620, 73735, 1023])
def test_get_block_instruments(
    block_id: int, db_connection: Connection, check_block: Callable[[_Block], None]
) -> None:
    block_repository = create_block_repository(db_connection)
    block = block_repository.get(block_id)
    observations = block["observations"]
    for i in range(len(observations)):
        assert "telescope_configurations" in observations[i]
        telescope_configs = observations[i]["telescope_configurations"]

        for j in range(len(telescope_configs)):
            assert "payload_configurations" in telescope_configs[j]
            payload_configs = telescope_configs[j]["payload_configurations"]

            for k in range(len(payload_configs)):
                assert "instruments" in payload_configs[k]
    check_block(block)


@nodatabase
@pytest.mark.parametrize(
    "block_id, expected_block_status",
    [
        (2339, "Expired"),
        (1, "On hold"),
    ],
)
def test_get_block_status(
    block_id: int, expected_block_status: str, db_connection: Connection
) -> None:
    block_repository = create_block_repository(db_connection)
    status = block_repository.get_block_status(block_id)

    assert expected_block_status == status["value"]


@nodatabase
def test_get_block_status_raises_error_for_wrong_block_id(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NoResultFound):
        block_repository.get_block_status(0)


@nodatabase
def test_update_block_status(db_connection: Connection) -> None:
    # Set the status to "On Hold" and the reason to "not needed"
    block_repository = create_block_repository(db_connection)
    block_id = 2339
    block_repository.update_block_status(block_id, "On hold", "not needed")
    block_status = block_repository.get_block_status(block_id)
    assert block_status["value"] == "On hold"
    assert block_status["reason"] == "not needed"

    # Now set it the status to "Active" and reason to "Awaiting driftscan"
    block_repository.update_block_status(block_id, "Active", "Awaiting driftscan")
    block_status = block_repository.get_block_status(block_id)
    assert block_status["value"] == "Active"
    assert block_status["reason"] == "Awaiting driftscan"


@nodatabase
def test_update_block_status_raises_error_for_wrong_block_id(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NotFoundError):
        block_repository.update_block_status(0, "Active", "")


@nodatabase
def test_update_block_status_raises_error_for_wrong_status(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(ValueError) as excinfo:
        block_repository.update_block_status(1, "Wrong block status", "")

    assert "block status" in str(excinfo.value)


@nodatabase
@pytest.mark.parametrize(
    "block_visit_id, expected_block_visit_status",
    [
        (5479, "Accepted"),
        (5457, "Rejected"),
    ],
)
def test_get_block_visit(
    block_visit_id: int, expected_block_visit_status: str, db_connection: Connection
) -> None:
    block_repository = create_block_repository(db_connection)
    block_visit = block_repository.get_block_visit(block_visit_id)
    assert block_visit_id == int(block_visit["id"])
    assert expected_block_visit_status == block_visit["status"]


@nodatabase
@pytest.mark.parametrize(
    "block_visit_id, expected_block_visit_status",
    [
        (1, "In queue"),
        (15, "Accepted"),
        (5457, "Rejected"),
    ],
)
def test_get_block_visit_status(
    block_visit_id: int, expected_block_visit_status: str, db_connection: Connection
) -> None:
    block_repository = create_block_repository(db_connection)
    status = block_repository.get_block_visit_status(block_visit_id)

    assert expected_block_visit_status == status


@nodatabase
def test_get_block_visit_status_raises_error_for_wrong_block_id(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NotFoundError):
        block_repository.get_block_visit_status(0)


@nodatabase
def test_get_block_visit_status_raises_error_for_deleted_status(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NotFoundError):
        block_repository.get_block_visit_status(829)


@nodatabase
def test_update_block_visit_status(db_connection: Connection) -> None:
    # Set the status to "Accepted"
    block_repository = create_block_repository(db_connection)
    block_visit_id = 2300  # The status for this block visit is "In queue"
    block_repository.update_block_visit_status(block_visit_id, "Accepted")
    assert block_repository.get_block_visit_status(block_visit_id) == "Accepted"

    # Now set it to "Rejected"
    block_repository.update_block_visit_status(block_visit_id, "Rejected")
    assert block_repository.get_block_visit_status(block_visit_id) == "Rejected"


@nodatabase
def test_update_block_visit_status_can_be_repeated(db_connection: Connection) -> None:
    # Set the status to "Accepted"
    block_repository = create_block_repository(db_connection)
    block_visit_id = 2300  # The status for this block visit is "In queue"
    block_repository.update_block_visit_status(block_visit_id, "Accepted")
    assert block_repository.get_block_visit_status(block_visit_id) == "Accepted"

    # Now set it to "Accepted" again
    block_repository.update_block_visit_status(block_visit_id, "Accepted")
    assert block_repository.get_block_visit_status(block_visit_id) == "Accepted"


@nodatabase
def test_update_block_visit_status_raises_error_for_wrong_block_id(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NotFoundError):
        block_repository.update_block_visit_status(0, "Accepted")


@nodatabase
def test_update_block_visit_status_raises_error_for_deleted_block_status(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(NotFoundError):
        block_repository.update_block_visit_status(1234567890, "Deleted")


@nodatabase
def test_update_block_visit_status_raises_error_for_wrong_status(
    db_connection: Connection,
) -> None:
    block_repository = create_block_repository(db_connection)
    with pytest.raises(ValueError) as excinfo:
        block_repository.update_block_visit_status(1, "Wrong block visit status")
    assert "block visit status" in str(excinfo.value)
