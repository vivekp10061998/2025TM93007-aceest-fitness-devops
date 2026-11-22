"""Program data adapted from the supplied ACEest desktop versions."""
PROGRAMS = {
    "fat-loss": {
        "id": "fat-loss",
        "name": "Fat Loss (FL)",
        "focus": "Cardio, resistance training and recovery",
        "weekly_plan": ["Strength", "Interval cardio", "Upper body", "Lower body", "Active recovery"],
        "calorie_factor": 22,
    },
    "muscle-gain": {
        "id": "muscle-gain",
        "name": "Muscle Gain (MG)",
        "focus": "Progressive overload and adequate recovery",
        "weekly_plan": ["Squats", "Bench press", "Deadlifts", "Overhead press", "Rows"],
        "calorie_factor": 30,
    },
    "endurance": {
        "id": "endurance",
        "name": "Endurance (EN)",
        "focus": "Aerobic conditioning and gradual volume",
        "weekly_plan": ["Zone 2 run", "Intervals", "Cross training", "Tempo", "Recovery"],
        "calorie_factor": 28,
    },
}
