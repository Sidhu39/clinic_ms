from app import create_app, db
from flask_migrate import Migrate
from app.models import User, PatientVisit

app = create_app()
migrate = Migrate(app, db)
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Appointment': PatientVisit}

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5000)
