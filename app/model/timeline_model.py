from typing import Optional, List
import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# Result from select sql\nfrom sqlite_master\nwhere type = "table"\norder by name
# Used for database schema validation
# IMPORTANT: CHANGE WHEN MODIFYING THE SCHEMA
SCHEMA_TABLE_SQL_VAL = [
    """CREATE TABLE high_level_events (
	id INTEGER NOT NULL, 
	date_time_min DATETIME NOT NULL, 
	date_time_max DATETIME NOT NULL, 
	event_type VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	reasoning_description VARCHAR NOT NULL, 
	reasoning_reference VARCHAR NOT NULL, 
	test_event_type VARCHAR NOT NULL, 
	test_event_evidence VARCHAR NOT NULL, 
	user_comments VARCHAR, 
	low_level_events_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(low_level_events_id) REFERENCES low_level_events (id)
)""",
"""CREATE TABLE keys (
	id INTEGER NOT NULL, 
	key_name VARCHAR NOT NULL, 
	key_value VARCHAR NOT NULL, 
	high_level_events_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(high_level_events_id) REFERENCES high_level_events (id)
)""",
"""CREATE TABLE labels (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)""",
"""CREATE TABLE labels_high_level_events (
	labels_id INTEGER NOT NULL, 
	high_level_events_id INTEGER NOT NULL, 
	PRIMARY KEY (labels_id, high_level_events_id), 
	FOREIGN KEY(labels_id) REFERENCES labels (id), 
	FOREIGN KEY(high_level_events_id) REFERENCES high_level_events (id)
)""",
"""CREATE TABLE labels_low_level_events (
	labels_id INTEGER NOT NULL, 
	low_level_events_id INTEGER NOT NULL, 
	PRIMARY KEY (labels_id, low_level_events_id), 
	FOREIGN KEY(labels_id) REFERENCES labels (id), 
	FOREIGN KEY(low_level_events_id) REFERENCES low_level_events (id)
)""",
"""CREATE TABLE low_level_events (
	id INTEGER NOT NULL, 
	date_time_min DATETIME NOT NULL, 
	date_time_max DATETIME NOT NULL, 
	event_type VARCHAR NOT NULL, 
	path VARCHAR NOT NULL, 
	evidence VARCHAR NOT NULL, 
	plugin VARCHAR NOT NULL, 
	provenance_raw_entry VARCHAR NOT NULL, 
	keys VARCHAR, 
	user_comments VARCHAR, 
	PRIMARY KEY (id)
)""",
"""CREATE TABLE supporting_after (
	low_level_events_id INTEGER NOT NULL, 
	high_level_events_id INTEGER NOT NULL, 
	PRIMARY KEY (low_level_events_id, high_level_events_id), 
	FOREIGN KEY(low_level_events_id) REFERENCES low_level_events (id), 
	FOREIGN KEY(high_level_events_id) REFERENCES high_level_events (id)
)""",
"""CREATE TABLE supporting_before (
	low_level_events_id INTEGER NOT NULL, 
	high_level_events_id INTEGER NOT NULL, 
	PRIMARY KEY (low_level_events_id, high_level_events_id), 
	FOREIGN KEY(low_level_events_id) REFERENCES low_level_events (id), 
	FOREIGN KEY(high_level_events_id) REFERENCES high_level_events (id)
)""",
]

class Base(DeclarativeBase):
    pass

# Many to many relationships
supporting_before_table = Table(
    "supporting_before",
    Base.metadata,
    Column("low_level_events_id", ForeignKey("low_level_events.id"), primary_key=True),
    Column("high_level_events_id", ForeignKey("high_level_events.id"), primary_key=True)
)

supporting_after_table = Table(
    "supporting_after",
    Base.metadata,
    Column("low_level_events_id", ForeignKey("low_level_events.id"), primary_key=True),
    Column("high_level_events_id", ForeignKey("high_level_events.id"), primary_key=True)
)

labels_high_level_events_table = Table(
    "labels_high_level_events",
    Base.metadata,
    Column("labels_id", ForeignKey("labels.id"), primary_key=True),
    Column("high_level_events_id", ForeignKey("high_level_events.id"), primary_key=True)
)

labels_low_level_events_table = Table(
    "labels_low_level_events",
    Base.metadata,
    Column("labels_id", ForeignKey("labels.id"), primary_key=True),
    Column("low_level_events_id", ForeignKey("low_level_events.id"), primary_key=True)
)

class LowLevelEvents(Base):
    __tablename__ = "low_level_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    # One to one
    high_level_events: Mapped["HighLevelEvents"] = relationship(back_populates="low_level_events")
    # Many to many, supporting evidences
    supporting_after: Mapped[Optional[List["HighLevelEvents"]]] = relationship(secondary=supporting_after_table, back_populates="supporting_after")
    supporting_before: Mapped[Optional[List["HighLevelEvents"]]] = relationship(secondary=supporting_before_table, back_populates="supporting_before")
    date_time_min: Mapped[datetime.datetime]
    date_time_max: Mapped[datetime.datetime]
    event_type: Mapped[str]
    path: Mapped[str]
    evidence: Mapped[str]
    plugin: Mapped[str]
    provenance_raw_entry: Mapped[str]
    keys: Mapped[Optional[str]] # TODO: Remove optional once low_level_event keys variable is used by dftpl
    user_comments: Mapped[Optional[str]]
    # Many to many, labels
    labels: Mapped[Optional[List["Labels"]]] = relationship(secondary=labels_low_level_events_table, back_populates="low_level_events")

class HighLevelEvents(Base):
    __tablename__ = "high_level_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    date_time_min: Mapped[datetime.datetime]
    date_time_max: Mapped[datetime.datetime]
    event_type: Mapped[str]
    description: Mapped[str]
    category: Mapped[str] # analyser category
    reasoning_description: Mapped[str]
    reasoning_reference: Mapped[str]
    test_event_type: Mapped[str]
    test_event_evidence: Mapped[str]
    user_comments: Mapped[Optional[str]]
    # One to one, which low level event this high level event belongs to
    low_level_events_id: Mapped[int] = mapped_column(ForeignKey("low_level_events.id"))
    low_level_events: Mapped["LowLevelEvents"] = relationship(back_populates="high_level_events", single_parent=True)
    # Many to many, supporting low level event evidences and labels
    supporting_after: Mapped[Optional[List["LowLevelEvents"]]] = relationship(secondary=supporting_after_table, back_populates="supporting_after")
    supporting_before: Mapped[Optional[List["LowLevelEvents"]]] = relationship(secondary=supporting_before_table, back_populates="supporting_before")
    labels: Mapped[Optional[List["Labels"]]] = relationship(secondary=labels_high_level_events_table, back_populates="high_level_events")
    # One to many, key values stored separately
    keys: Mapped[Optional[List["Keys"]]] = relationship(back_populates="high_level_events")

class Labels(Base):
    __tablename__ = "labels"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # Many to many
    low_level_events: Mapped[Optional[List["LowLevelEvents"]]] = relationship(secondary=labels_low_level_events_table, back_populates="labels")
    high_level_events: Mapped[Optional[List["HighLevelEvents"]]] = relationship(secondary=labels_high_level_events_table, back_populates="labels")

class Keys(Base):
    __tablename__ = "keys"
    id: Mapped[int] = mapped_column(primary_key=True)
    key_name: Mapped[str]
    key_value: Mapped[str]
    # Many to one
    high_level_events_id: Mapped[int] = mapped_column(ForeignKey("high_level_events.id"))
    high_level_events: Mapped["HighLevelEvents"] = relationship(back_populates="keys")
