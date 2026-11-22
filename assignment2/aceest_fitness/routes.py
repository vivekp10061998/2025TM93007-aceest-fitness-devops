"""REST endpoints for ACEest member management and training plans."""
from flask import Blueprint, current_app, jsonify, render_template, request
from sqlalchemy.exc import IntegrityError

from .catalog import PROGRAMS
from .models import Member, Progress, db

api = Blueprint("api", __name__)


def _json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def _validate_member(data, updating=False):
    if data is None:
        return "Expected a JSON object"
    required = {"name", "email", "age", "weight_kg", "program"}
    if not updating and not required.issubset(data):
        return "Missing required member fields"
    if not updating and not data:
        return "Member details required"
    if "name" in data and (not isinstance(data["name"], str) or not 2 <= len(data["name"].strip()) <= 100):
        return "Name must contain 2 to 100 characters"
    if "email" in data and (not isinstance(data["email"], str) or "@" not in data["email"] or len(data["email"]) > 255):
        return "A valid email is required"
    if "age" in data and (type(data["age"]) is not int or not 12 <= data["age"] <= 100):
        return "Age must be an integer between 12 and 100"
    if "weight_kg" in data and (type(data["weight_kg"]) not in (int, float) or not 20 <= data["weight_kg"] <= 400):
        return "Weight must be between 20 and 400 kg"
    if "program" in data and data["program"] not in PROGRAMS:
        return "Unknown fitness program"
    if not set(data).issubset(required):
        return "Unsupported member fields"
    return None


def _member_or_404(member_id):
    member = db.session.get(Member, member_id)
    if member is None:
        return None
    return member


@api.get("/")
def homepage():
    return render_template("index.html", version=current_app.config["APP_VERSION"])


@api.get("/api/version")
def version():
    return jsonify(application="ACEest Fitness & Gym", version=current_app.config["APP_VERSION"], variant=current_app.config["APP_VARIANT"])


@api.get("/api/programs")
def programs():
    return jsonify(programs=list(PROGRAMS.values()))


@api.get("/api/members")
def list_members():
    members = db.session.execute(db.select(Member).order_by(Member.id)).scalars().all()
    return jsonify(members=[member.to_dict() for member in members], count=len(members))


@api.post("/api/members")
def add_member():
    body = _json_body()
    error = _validate_member(body)
    if error:
        return jsonify(error=error), 400
    member = Member(
        name=body["name"].strip(),
        email=body["email"].strip().lower(),
        age=body["age"],
        weight_kg=body["weight_kg"],
        program=body["program"],
    )
    db.session.add(member)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Email already registered"), 409
    return jsonify(member=member.to_dict()), 201


@api.get("/api/members/<int:member_id>")
def get_member(member_id):
    member = _member_or_404(member_id)
    return (jsonify(member=member.to_dict()), 200) if member else (jsonify(error="Member not found"), 404)


@api.patch("/api/members/<int:member_id>")
def update_member(member_id):
    member = _member_or_404(member_id)
    if member is None:
        return jsonify(error="Member not found"), 404
    body = _json_body()
    error = _validate_member(body, updating=True)
    if error:
        return jsonify(error=error), 400
    for key, value in body.items():
        if key in ("name", "email"):
            value = value.strip()
            if key == "email":
                value = value.lower()
        setattr(member, key, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Email already registered"), 409
    return jsonify(member=member.to_dict())


@api.delete("/api/members/<int:member_id>")
def delete_member(member_id):
    member = _member_or_404(member_id)
    if member is None:
        return jsonify(error="Member not found"), 404
    db.session.delete(member)
    db.session.commit()
    return "", 204


@api.get("/api/members/<int:member_id>/progress")
def get_progress(member_id):
    if _member_or_404(member_id) is None:
        return jsonify(error="Member not found"), 404
    entries = db.session.execute(
        db.select(Progress).where(Progress.member_id == member_id).order_by(Progress.id)
    ).scalars().all()
    return jsonify(progress=[entry.to_dict() for entry in entries])


@api.post("/api/members/<int:member_id>/progress")
def record_progress(member_id):
    if _member_or_404(member_id) is None:
        return jsonify(error="Member not found"), 404
    body = _json_body()
    if body is None or type(body.get("adherence_percent")) is not int or not 0 <= body["adherence_percent"] <= 100:
        return jsonify(error="adherence_percent must be an integer from 0 to 100"), 400
    note = body.get("note", "")
    if not isinstance(note, str) or len(note) > 300:
        return jsonify(error="note must be up to 300 characters"), 400
    if set(body) - {"adherence_percent", "note"}:
        return jsonify(error="Unsupported progress fields"), 400
    progress = Progress(member_id=member_id, adherence_percent=body["adherence_percent"], note=note)
    db.session.add(progress)
    db.session.commit()
    return jsonify(progress=progress.to_dict()), 201


@api.get("/api/stats")
def stats():
    members = db.session.execute(db.select(Member)).scalars().all()
    return jsonify(total_members=len(members), programs={name: sum(m.program == name for m in members) for name in PROGRAMS})
