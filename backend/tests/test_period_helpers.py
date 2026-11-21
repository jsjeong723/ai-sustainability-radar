def test_bls_series_configuration():
    from app.collectors import BLS_SERIES
    assert "CES0000000001" in BLS_SERIES
    assert "LNS14000000" in BLS_SERIES
    assert "CES0500000003" in BLS_SERIES
