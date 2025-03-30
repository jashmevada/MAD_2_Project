from backend.utils.common import add_db
from ..models.model import  User

def create_initial_data():
    existing_user = User.query.filter(
        (User.username == "admin") | (User.email == "admin@admin.com")
    ).first()

    if existing_user:
        return 
    
    admin = User(username='admin', email='admin@admin.com', role='admin', password="admin")
    
    return add_db([admin])
