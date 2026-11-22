from aceest_fitness import create_app


def test_homepage_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest Fitness" in response.data


def test_liveness(client):
    assert client.get("/health/live").json["status"] == "alive"


def test_readiness(client):
    assert client.get("/health/ready").status_code == 200


def test_version(client):
    response = client.get("/api/version")
    assert response.json["version"] == "test-version"
    assert response.headers["X-ACEest-Version"] == "test-version"


def test_program_catalog(client):
    response = client.get("/api/programs")
    assert response.status_code == 200
    assert len(response.json["programs"]) == 3


def test_create_and_list_members(client, sample_member):
    response = client.post("/api/members", json=sample_member)
    assert response.status_code == 201
    assert response.json["member"]["estimated_daily_calories"] == 1727
    members = client.get("/api/members").json
    assert members["count"] == 1
    assert members["members"][0]["name"] == "Aarav Patil"


def test_member_detail(client, sample_member):
    member_id = client.post("/api/members", json=sample_member).json["member"]["id"]
    assert client.get(f"/api/members/{member_id}").json["member"]["email"] == "aarav@example.com"


def test_duplicate_email(client, sample_member):
    client.post("/api/members", json=sample_member)
    duplicate = dict(sample_member, email="AARAV@example.com")
    assert client.post("/api/members", json=duplicate).status_code == 409


def test_invalid_age(client, sample_member):
    assert client.post("/api/members", json=dict(sample_member, age=10)).status_code == 400


def test_invalid_program(client, sample_member):
    assert client.post("/api/members", json=dict(sample_member, program="unknown")).status_code == 400


def test_invalid_weight(client, sample_member):
    assert client.post("/api/members", json=dict(sample_member, weight_kg=4)).status_code == 400


def test_missing_fields(client):
    assert client.post("/api/members", json={"name": "A"}).status_code == 400


def test_non_json_body(client):
    assert client.post("/api/members", data="bad").status_code == 400


def test_patch_member(client, sample_member):
    member_id = client.post("/api/members", json=sample_member).json["member"]["id"]
    update = client.patch(f"/api/members/{member_id}", json={"weight_kg": 80, "program": "muscle-gain"})
    assert update.status_code == 200
    assert update.json["member"]["estimated_daily_calories"] == 2400


def test_patch_rejects_unknown_field(client, sample_member):
    member_id = client.post("/api/members", json=sample_member).json["member"]["id"]
    assert client.patch(f"/api/members/{member_id}", json={"admin": True}).status_code == 400


def test_delete_member(client, sample_member):
    member_id = client.post("/api/members", json=sample_member).json["member"]["id"]
    assert client.delete(f"/api/members/{member_id}").status_code == 204
    assert client.get(f"/api/members/{member_id}").status_code == 404


def test_not_found(client):
    assert client.get("/api/members/999").status_code == 404


def test_progress_log(client, sample_member):
    member_id = client.post("/api/members", json=sample_member).json["member"]["id"]
    response = client.post(f"/api/members/{member_id}/progress", json={"adherence_percent": 85, "note": "Good week"})
    assert response.status_code == 201
    logs = client.get(f"/api/members/{member_id}/progress").json["progress"]
    assert logs[0]["adherence_percent"] == 85


def test_invalid_progress(client, sample_member):
    member_id = client.post("/api/members", json=sample_member).json["member"]["id"]
    assert client.post(f"/api/members/{member_id}/progress", json={"adherence_percent": 140}).status_code == 400


def test_stats(client, sample_member):
    client.post("/api/members", json=sample_member)
    stats = client.get("/api/stats").json
    assert stats["total_members"] == 1
    assert stats["programs"]["fat-loss"] == 1


def test_shadow_mode_blocks_mutations(tmp_path, sample_member):
    app = create_app({
        "TESTING": True,
        "SHADOW_MODE": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'shadow.db'}",
    })
    client = app.test_client()
    assert client.post("/api/members", json=sample_member).status_code == 204
    assert client.get("/api/members").json["count"] == 0


def test_invalid_404(client):
    assert client.get("/non-existent").status_code == 404
