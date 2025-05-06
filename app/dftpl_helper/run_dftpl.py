# Functions to run DFTPL. Based on "dftpl.py" branch "python-analysers" (as of 03052025)
from app import current_app
from app.model.timeline_model import Base
from json import dump # Dump to file

from secrets import token_hex  # Generate random file name
from os.path import join
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import session

from dftpl.reader.CSVReader import CSVReader
from dftpl.timelines.LowLevelTimeline import LowLevelTimeline
from dftpl.timelines.HighLevelTimeline import HighLevelTimeline, MergeHighLevelTimeline
from dftpl.events.LowLevelEvent import LowLevelEvent
from dftpl.events.HighLevelEvent import HighLevelEvent

# Import all dftpl analysers by default
# Update the list of usable analysers to match dftpl
# TEST: Only imported analysers needed for testing
# TODO: Add a function in dftpl to generate:
# 1. dictionary mapping of all analyser classes
# 2. update analysers.json list of all analysers
import dftpl.analyzers.useractivity.FileDownloads as FileDownloads
import dftpl.analyzers.useractivity.RecentFileAccess as RecentFileAccess

# import dftpl.analyzers.useractivity.SoftwareInstallation as SoftwareInstallation
import dftpl.analyzers.useractivity.USBConnectedRegDeviceClasses as USBConnectedRegDeviceClasses
import dftpl.analyzers.useractivity.USBConnectedRegUSB as USBConnectedRegUSB
import dftpl.analyzers.useractivity.USBConnectedRegUSBSTOR as USBConnectedRegUSBSTOR
import dftpl.analyzers.useractivity.USBConnectedWinevt as USBConnectedWinevt
import dftpl.analyzers.useractivity.WindowsEventLogCleared as WindowsEventLogCleared
import dftpl.analyzers.useractivity.WindowsFirewallDisabled as WindowsFirewallDisabled
import dftpl.analyzers.web.AllImagesFromCache as AllImagesFromCache

# import dftpl.analyzers.web.AllVideoFromCache as AllVideoFromCache
import dftpl.analyzers.web.BingSearch as BingSearch
import dftpl.analyzers.web.GoogleSearch as GoogleSearch
import dftpl.analyzers.web.WebVisits as WebVisits
import dftpl.analyzers.windows.LastShutdown as LastShutdown
import dftpl.analyzers.windows.ProcessCreation as ProcessCreation
import dftpl.analyzers.windows.ProgramOpened as ProgramOpened

# Default analysers list, made a const for multiple functions
DEFAULT_analyserS = {
    FileDownloads.description: FileDownloads,
    RecentFileAccess.description: RecentFileAccess,
    USBConnectedRegDeviceClasses.description: USBConnectedRegDeviceClasses,
    USBConnectedRegUSB.description: USBConnectedRegUSB,
    USBConnectedRegUSBSTOR.description: USBConnectedRegUSBSTOR,
    USBConnectedWinevt.description: USBConnectedWinevt,
    WindowsEventLogCleared.description: WindowsEventLogCleared,
    WindowsFirewallDisabled.description: WindowsFirewallDisabled,
    AllImagesFromCache.description: AllImagesFromCache,
    BingSearch.description: BingSearch,
    GoogleSearch.description: GoogleSearch,
    WebVisits.description: WebVisits,
    LastShutdown.description: LastShutdown,
    ProcessCreation.description: ProcessCreation,
    ProgramOpened.description: ProgramOpened,
}


# Generate an updated analysers.json file
# Call on startup
def generate_analysers_list():
    analyser_list = {"analysers-list": []}
    # TODO: Make a template class for all analysers
    for analyser in DEFAULT_analyserS.values():
        analyser_list["analysers-list"].append(
            {"name": analyser.description, "category": analyser.analyser_category}
        )
    try:
        with open(join(current_app.config["APP_DIR"], "dftpl_helper", "analysers.json"), "w", encoding="utf-8") as f:
            dump(analyser_list, f, ensure_ascii=False, indent=4)
    except OSError:
        # HACK: LOGGING PLS
        print("ERROR: Writing analysers.json")

# Create and store timeline data in sqlite db
# User can change the default name when they download it
def store_timelines(low_timeline: LowLevelTimeline, high_timeline: HighLevelTimeline):
    # Create DB using model
    engine = create_engine(
        (
            "sqlite:///"
            + current_app.config["UPLOAD_DIR"]
            + "\\"
            + token_hex(16)
            + ".sqlite"
        ),
        echo=True,
    )
    Base.metadata.create_all(engine)
    # Write both high level and low level timelines to db
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    # Iterate over low level events and write to DB

    # Iterate over high level events and write to DB

    # Save and close DB connection
    db_session.remove()
    engine.dispose()


# analysers_arr = List of names based on the analysers's description variable
def run_dftpl(input_file_path: str, analysers_arr: list[str]):
    # Read the CSV file
    print("Reading CSV file ...")
    reader = CSVReader(input_file_path)

    # Create a list of LowLevelEvent objects
    print("Creating low-level timeline ...")
    low_timeline = LowLevelTimeline()
    low_timeline.create_timeline(reader)

    # Create a list of high-level timeline
    high_timelines = []

    # Get list of search analysers selected by users, if empty default to all
    selected_analysers = []
    for selected in analysers_arr:
        selected_analysers.append(
            DEFAULT_analyserS.get(selected, DEFAULT_analyserS.values)
        )

    # Run each search analyser
    for analyser in selected_analysers:
        print(f"Running {analyser.description} analyser ...")
        high_timeline = analyser.Run(low_timeline)
        if high_timeline:
            high_timelines.append(high_timeline)

    # Merge the high-level timelines
    print("Merging high-level timelines ...")
    merge_timelines = MergeHighLevelTimeline(high_timelines)
    merged_high_timelines = merge_timelines.merge()

    # Writing to database
    store_timelines(low_timeline=low_timeline, high_timeline=merged_high_timelines)
