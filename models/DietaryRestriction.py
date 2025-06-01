from sqlalchemy import Column, Integer, String, ForeignKey
from models import Base

class DietaryRestriction(Base):
    __tablename__ = "dietaryrestriction"
    dietaryrestrictionid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
class UserDietaryRestriction(Base):
    __tablename__ = "userdietaryrestriction"
    userdietaryrestrictionid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)
    dietaryrestrictionid = Column(Integer, ForeignKey("dietaryrestriction.dietaryrestrictionid"), nullable=False)