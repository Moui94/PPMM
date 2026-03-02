# backend/routes package
from .auth      import auth_bp
from .orders    import orders_bp
from .operations import operations_bp
from .quality   import quality_bp
from .users     import users_bp
from .export    import export_bp

ALL_BLUEPRINTS = [auth_bp, orders_bp, operations_bp, quality_bp, users_bp, export_bp]
