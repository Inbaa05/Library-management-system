"""Flask extensions, initialized without the app object."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

# JWT is handled manually with PyJWT to keep things simple
# We store a small helper here
class jwt:  # noqa: N801
    """Placeholder namespace; actual JWT logic is in utils/auth.py."""
    pass
