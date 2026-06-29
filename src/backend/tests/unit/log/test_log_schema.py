import uuid
import pytest
from datetime import datetime, timezone

from app.api.log.schema import LogQueryParams, LogEntryData, LogListData, LogStatsData, LevelCountData, TypeCountData


def test_log_query_params_defaults():
    params = LogQueryParams()

    assert params.page == 1
    assert params.page_size == 50
    assert params.log_type is None
    assert params.level is None
    assert params.user_id is None
    assert params.request_id is None
    assert params.action is None
    assert params.path is None
    assert params.start is None
    assert params.end is None


def test_log_query_params_page_size_clamped_to_max():
    params = LogQueryParams(page_size=999)

    assert params.page_size == 200


def test_log_query_params_page_size_clamped_to_min():
    params = LogQueryParams(page_size=0)

    assert params.page_size == 1


def test_log_query_params_page_size_negative_clamped():
    params = LogQueryParams(page_size=-5)

    assert params.page_size == 1


def test_log_query_params_page_clamped_to_min():
    params = LogQueryParams(page=0)

    assert params.page == 1


def test_log_query_params_page_negative_clamped():
    params = LogQueryParams(page=-3)

    assert params.page == 1


def test_log_query_params_valid_page_size():
    params = LogQueryParams(page_size=100)

    assert params.page_size == 100


def test_log_query_params_valid_page():
    params = LogQueryParams(page=5)

    assert params.page == 5


def test_log_query_params_boundary_page_size_1():
    params = LogQueryParams(page_size=1)

    assert params.page_size == 1


def test_log_query_params_boundary_page_size_200():
    params = LogQueryParams(page_size=200)

    assert params.page_size == 200


def test_log_query_params_with_all_filters():
    uid = uuid.uuid4()
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 12, 31, tzinfo=timezone.utc)

    params = LogQueryParams(
        log_type="http",
        level="ERROR",
        user_id=uid,
        request_id="req-123",
        action="board.create",
        path="/api/v1/boards",
        start=start,
        end=end,
        page=2,
        page_size=25,
    )

    assert params.log_type == "http"
    assert params.level == "ERROR"
    assert params.user_id == uid
    assert params.request_id == "req-123"
    assert params.action == "board.create"
    assert params.path == "/api/v1/boards"
    assert params.start == start
    assert params.end == end
    assert params.page == 2
    assert params.page_size == 25


def test_log_entry_data_minimal():
    entry = LogEntryData(
        id=1,
        timestamp=datetime.now(timezone.utc),
        log_type="application",
        level="INFO",
        logger_name="app.test",
        message="Test message",
    )

    assert entry.id == 1
    assert entry.user_id is None
    assert entry.request_id is None
    assert entry.method is None
    assert entry.path is None
    assert entry.status_code is None
    assert entry.duration_ms is None
    assert entry.ip_address is None
    assert entry.user_agent is None
    assert entry.action is None
    assert entry.resource_type is None
    assert entry.resource_id is None
    assert entry.extra is None


def test_log_entry_data_full():
    uid = uuid.uuid4()
    ts = datetime.now(timezone.utc)

    entry = LogEntryData(
        id=42,
        timestamp=ts,
        log_type="audit",
        level="WARNING",
        logger_name="app.audit",
        message="User updated board",
        user_id=uid,
        request_id="req-xyz",
        method="PATCH",
        path="/api/v1/boards/123",
        status_code=200,
        duration_ms=120.5,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        action="board.update",
        resource_type="board",
        resource_id="123",
        extra={"old_title": "Old", "new_title": "New"},
    )

    assert entry.id == 42
    assert entry.log_type == "audit"
    assert entry.user_id == uid
    assert entry.extra == {"old_title": "Old", "new_title": "New"}


def test_log_list_data():
    data = LogListData(
        logs=[],
        total=0,
        page=1,
        page_size=50,
        total_pages=0,
    )

    assert data.logs == []
    assert data.total == 0
    assert data.total_pages == 0


def test_log_stats_data():
    stats = LogStatsData(
        total_count=50,
        level_counts=[LevelCountData(level="INFO", count=50)],
        type_counts=[TypeCountData(log_type="http", count=50)],
        error_rate=0.0,
        start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end=datetime(2026, 12, 31, tzinfo=timezone.utc),
    )

    assert stats.total_count == 50
    assert len(stats.level_counts) == 1
    assert stats.level_counts[0].level == "INFO"
    assert len(stats.type_counts) == 1
    assert stats.type_counts[0].log_type == "http"
    assert stats.error_rate == 0.0


def test_level_count_data():
    lc = LevelCountData(level="ERROR", count=10)

    assert lc.level == "ERROR"
    assert lc.count == 10


def test_type_count_data():
    tc = TypeCountData(log_type="audit", count=5)

    assert tc.log_type == "audit"
    assert tc.count == 5
