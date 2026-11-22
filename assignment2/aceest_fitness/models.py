"""Simple persistent member and progress models for demo use."""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    program = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    progress_entries = db.relationship("Progress", cascade="all, delete-orphan", back_populates="member")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "weight_kg": self.weight_kg,
            "program": self.program,
            "estimated_daily_calories": round(self.weight_kg * _factor(self.program)),
        }


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    adherence_percent = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(300), nullable=False, default="")
    recorded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    member = db.relationship("Member", back_populates="progress_entries")

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "adherence_percent": self.adherence_percent,
            "note": self.note,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


def _factor(program):
    from .catalog import PROGRAMS
    return PROGRAMS[program]["calorie_factor"]
