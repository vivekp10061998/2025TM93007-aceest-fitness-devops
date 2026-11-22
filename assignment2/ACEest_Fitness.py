"""WSGI entry point for the ACEest Fitness & Gym web application."""
from aceest_fitness import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
