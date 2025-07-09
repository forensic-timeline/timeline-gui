from typing import Optional,List

from sqlalchemy import ForeignKey
from sqlalchemy import String
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
	    date_time_min VARCHAR NOT NULL,
		date_time_max VARCHAR,
		event_type VARCHAR NOT NULL,
		description VARCHAR NOT NULL,
		category VARCHAR NOT NULL,
		reasoning_description VARCHAR NOT NULL,
		reasoning_reference VARCHAR,
		test_event_type VARCHAR NOT NULL,
		test_event_evidence VARCHAR NOT NULL,
		user_comments VARCHAR,
		low_level_event_id INTEGER NOT NULL,
		PRIMARY KEY (id),
		FOREIGN KEY(low_level_event_id) REFERENCES low_level_events (id)
)""",
(
    'CREATE VIRTUAL TABLE high_level_events_idx USING FTS5 ('
        'id,date_time_min,date_time_max UNINDEXED,event_type,description,category,'
          'reasoning_description,reasoning_reference UNINDEXED,test_event_type,test_event_evidence,'
            'user_comments UNINDEXED,low_level_event_id,tokenize="porter unicode61" ,'
              'content=high_level_events,content_rowid=id)'
),
(
"""CREATE TABLE 'high_level_events_idx_config'(k PRIMARY KEY,v) WITHOUT ROWID"""
)
,
(
"""CREATE TABLE 'high_level_events_idx_data'(id INTEGER PRIMARY KEY,block BLOB)"""
)
,
(
"""CREATE TABLE 'high_level_events_idx_docsize'(id INTEGER PRIMARY KEY,sz BLOB)"""
)
,
(
"""CREATE TABLE 'high_level_events_idx_idx'(segid,term,pgno,PRIMARY KEY(segid,term)) WITHOUT ROWID"""
)
,
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
	FOREIGN KEY(labels_id) REFERENCES labels (id) ON DELETE CASCADE, 
	FOREIGN KEY(high_level_events_id) REFERENCES high_level_events (id) ON DELETE CASCADE
)""",
    """CREATE TABLE labels_low_level_events (
	labels_id INTEGER NOT NULL, 
	low_level_events_id INTEGER NOT NULL, 
	FOREIGN KEY(labels_id) REFERENCES labels (id) ON DELETE CASCADE, 
	FOREIGN KEY(low_level_events_id) REFERENCES low_level_events (id) ON DELETE CASCADE
)""",
    """CREATE TABLE low_level_events (
		id INTEGER NOT NULL,
		date_time_min VARCHAR NOT NULL,
		date_time_max VARCHAR,
		event_type VARCHAR NOT NULL,
		path VARCHAR NOT NULL,
		evidence VARCHAR NOT NULL,
		plugin VARCHAR NOT NULL,
		provenance_raw_entry VARCHAR NOT NULL,
		keys VARCHAR,
		user_comments VARCHAR,
		PRIMARY KEY (id)
)""",
(
"""CREATE VIRTUAL TABLE low_level_events_idx USING FTS5 (id,date_time_min,date_time_max UNINDEXED,event_type,path,evidence,plugin,provenance_raw_entry,keys UNINDEXED,user_comments UNINDEXED,tokenize="porter unicode61" ,content=low_level_events,content_rowid=id)"""
),
(
    "CREATE TABLE 'low_level_events_idx_config'(k PRIMARY KEY,v) " +
    "WITHOUT ROWID"
),
(
    "CREATE TABLE 'low_level_events_idx_data'(id INTEGER PRIMARY KEY,block BLOB)"
),
(
    "CREATE TABLE 'low_level_events_idx_docsize'(id INTEGER PRIMARY KEY,sz BLOB)"
),
(
    "CREATE TABLE 'low_level_events_idx_idx'(segid,term,pgno,PRIMARY KEY(segid,term)) " +
    "WITHOUT ROWID"
),
    """CREATE TABLE supporting_after (
	low_level_events_id INTEGER, 
	high_level_events_id INTEGER, 
	FOREIGN KEY(low_level_events_id) REFERENCES low_level_events (id), 
	FOREIGN KEY(high_level_events_id) REFERENCES high_level_events (id)
)""",
    """CREATE TABLE supporting_before (
	low_level_events_id INTEGER, 
	high_level_events_id INTEGER, 
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
    Column("low_level_events_id",ForeignKey("low_level_events.id")),
    Column(
        "high_level_events_id",ForeignKey("high_level_events.id")
    ),
)

supporting_after_table = Table(
    "supporting_after",
    Base.metadata,
    Column("low_level_events_id",ForeignKey("low_level_events.id")),
    Column(
        "high_level_events_id",ForeignKey("high_level_events.id")
    ),
)

labels_high_level_events_table = Table(
    "labels_high_level_events",
    Base.metadata,
    Column("labels_id",ForeignKey("labels.id",ondelete="CASCADE"), nullable=False),
    Column(
        "high_level_events_id",ForeignKey("high_level_events.id",ondelete="CASCADE"), nullable=False
    ),
)

labels_low_level_events_table = Table(
    "labels_low_level_events",
    Base.metadata,
    Column("labels_id",ForeignKey("labels.id",ondelete="CASCADE"), nullable=False),
    Column("low_level_events_id",ForeignKey("low_level_events.id",ondelete="CASCADE"), nullable=False)
)


class LowLevelEvents(Base):
    __tablename__ = "low_level_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    # One to one
    high_level_event: Mapped["HighLevelEvents"] = relationship(
        back_populates="low_level_event"
    )
    # Many to many,supporting evidences
    supporting_after: Mapped[Optional[List["HighLevelEvents"]]] = relationship(
        secondary=supporting_after_table,back_populates="supporting_after"
    )
    supporting_before: Mapped[Optional[List["HighLevelEvents"]]] = relationship(
        secondary=supporting_before_table,back_populates="supporting_before"
    )
    # HACK: Handling '0000-00-00T00:00:00.000000+00:00' by storing raw string
    date_time_min: Mapped[str]
    date_time_max: Mapped[
        Optional[str]
    ]  # HACK: As of 06052025,date_time_max aren't used (always "None")
    event_type: Mapped[str]
    path: Mapped[str]
    evidence: Mapped[str]
    plugin: Mapped[str]
    provenance_raw_entry: Mapped[str]
    keys: Mapped[
        Optional[str]
    ]  # HACK: As of 06052025,keys aren't used (always "None")
    user_comments: Mapped[Optional[str]]
    # Many to many,labels
    # FIXME: Cascade deleted labels
    labels: Mapped[Optional[List["Labels"]]] = relationship(
        secondary=labels_low_level_events_table,back_populates="low_level_events"
    )


class HighLevelEvents(Base):
    __tablename__ = "high_level_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    # HACK: Handling '0000-00-00T00:00:00.000000+00:00' by storing raw string
    date_time_min: Mapped[str]
    date_time_max: Mapped[Optional[str]]
    event_type: Mapped[str]
    description: Mapped[str]
    category: Mapped[str]  # analyser category
    reasoning_description: Mapped[str]
    reasoning_reference: Mapped[
        Optional[str]
    ]  # HACK: As of 06052025,some analysers doesn't have references
    test_event_type: Mapped[str]
    test_event_evidence: Mapped[str]
    user_comments: Mapped[Optional[str]]
    # One to one,which low level event this high level event belongs to
    low_level_event_id: Mapped[int] = mapped_column(ForeignKey("low_level_events.id"))
    low_level_event: Mapped["LowLevelEvents"] = relationship(
        back_populates="high_level_event",single_parent=True
    )
    # Many to many,supporting low level event evidences and labels
    supporting_after: Mapped[Optional[List["LowLevelEvents"]]] = relationship(
        secondary=supporting_after_table,back_populates="supporting_after"
    )
    supporting_before: Mapped[Optional[List["LowLevelEvents"]]] = relationship(
        secondary=supporting_before_table,back_populates="supporting_before"
    )
    # FIXME: Cascade deleted labels
    labels: Mapped[Optional[List["Labels"]]] = relationship(
        secondary=labels_high_level_events_table,back_populates="high_level_events"
    )
    # One to many,key values stored separately
    keys: Mapped[Optional[List["Keys"]]] = relationship(
        back_populates="high_level_events"
    )


# FIXME: Cascade deleted labels
class Labels(Base):
    __tablename__ = "labels"
    id: Mapped[int] = mapped_column(primary_key=True)
    # FIXME: Labels can be duplicate
    name: Mapped[str] = mapped_column(String())
    # Many to many
    low_level_events: Mapped[Optional[List["LowLevelEvents"]]] = relationship(
        secondary=labels_low_level_events_table,back_populates="labels",cascade="all"
    )
    high_level_events: Mapped[Optional[List["HighLevelEvents"]]] = relationship(
        secondary=labels_high_level_events_table,back_populates="labels",cascade="all"
    )


class Keys(Base):
    __tablename__ = "keys"
    id: Mapped[int] = mapped_column(primary_key=True)
    key_name: Mapped[str]
    key_value: Mapped[str]
    # Many to one
    high_level_events_id: Mapped[int] = mapped_column(
        ForeignKey("high_level_events.id")
    )
    high_level_events: Mapped["HighLevelEvents"] = relationship(back_populates="keys")
