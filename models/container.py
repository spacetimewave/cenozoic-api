from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from models.base import Base
import enum
from sqlalchemy import Enum as SqlEnum 

class ContainerStatus(enum.Enum):
    stopped = "stopped"
    running = "running"

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    container_id = Column(String, unique=True, index=True)  # Docker container ID
    container_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SqlEnum(ContainerStatus), default=ContainerStatus.stopped, nullable=False)

    # Define the relationship back to User
    owner = relationship("User", back_populates="containers")
