"""
Created on Aug 2025
@author: Yara
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
import json

class DBConn:
    def __init__(self, db_label: str = "main"):
        self.db_label = db_label
        self.session: Session = None
        self.engine = None
        self.db_config = self._load_db_config()

    def _load_db_config(self):
        """Load DB config from environment (scalable to multiple DBs)."""
        db_config = {
            "main": {
                "driver": os.getenv("DB_DRIVER", "mysql+pymysql"),
                "user": os.getenv("DB_USER", "car_user"),
                "pwd": os.getenv("DB_PASSWORD", "car_pass"), #hardcoded password and credentials just for the challenge. In real-case scenario use ENV VAR
                "addr": os.getenv("DB_HOST", "db"),
                "port": os.getenv("DB_PORT", "3306"),
                "db_name": os.getenv("DB_NAME", "cars"),
                "pool_size": int(os.getenv("DB_POOL_SIZE", "15")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
                "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
            }
        }
        return db_config

    def connect(self):
        """Open DB engine + session with connection pool."""
        if self.session is not None:
            return self.session

        s = self.db_config[self.db_label]
        conn_str = f"{s['driver']}://{s['user']}:{s['pwd']}@{s['addr']}:{s['port']}/{s['db_name']}"

        self.engine = create_engine(
            conn_str,
            poolclass=QueuePool,
            pool_size=s["pool_size"],
            max_overflow=s["max_overflow"],
            pool_recycle=s["pool_recycle"],
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()
        return self.session

    def disconnect(self):
        if self.session:
            self.session.close()
            self.session = None

    def add(self, dao_obj):
        self.session.add(dao_obj)

    def commit(self):
        self.session.commit()

    def save(self, dao_obj):
        self.add(dao_obj)
        self.commit()

    def delete(self, dao_obj):
        self.session.delete(dao_obj)
        self.commit()
