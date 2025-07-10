# Functions to run DFTPL. Based on "dftpl.py" branch "python-analysers" (as of 03052025)
from json import dump  # Dump to file
from os.path import join  # Construct path name
from os import remove
from secrets import token_hex  # Generate random file name
from flask.sessions import SessionMixin

# Import all dftpl analysers by default
# Update the list of usable analysers to match dftpl
# TODO: Add a function in dftpl to generate:
# 1. dictionary mapping of all analyser classes
# import dftpl.analyzers.useractivity.FileDownloads as FileDownloads
# import dftpl.analyzers.useractivity.RecentFileAccess as RecentFileAccess (Doesn't support dict of test events)
# import dftpl.analyzers.useractivity.SoftwareInstallation as SoftwareInstallation
import dftpl.analyzers.useractivity.USBConnectedRegDeviceClasses as USBConnectedRegDeviceClasses
import dftpl.analyzers.useractivity.USBConnectedRegUSB as USBConnectedRegUSB
import dftpl.analyzers.useractivity.USBConnectedRegUSBSTOR as USBConnectedRegUSBSTOR
import dftpl.analyzers.useractivity.USBConnectedWinevt as USBConnectedWinevt
import dftpl.analyzers.useractivity.WindowsEventLogCleared as WindowsEventLogCleared
import dftpl.analyzers.useractivity.WindowsFirewallDisabled as WindowsFirewallDisabled
import dftpl.analyzers.web.AllImagesFromCache as AllImagesFromCache
# import dftpl.analyzers.web.AllVideoFromCache as AllVideoFromCache
# import dftpl.analyzers.web.BingSearch as BingSearch
# import dftpl.analyzers.web.GoogleSearch as GoogleSearch # Null key value due to regex capturing wrong descriptions
import dftpl.analyzers.web.WebVisits as WebVisits
import dftpl.analyzers.windows.DefaultBrowser as DefaultBrowser
import dftpl.analyzers.windows.DeviceInstallation as DeviceInstallation
import dftpl.analyzers.windows.FailedLogin as FailedLogin
import dftpl.analyzers.windows.FileMRURegistry as FileMRURegistry
import dftpl.analyzers.windows.LastExecutedBAM as LastExecutedBAM
import dftpl.analyzers.windows.LastExecutedPCA as LastExecutedPCA
import dftpl.analyzers.windows.LastExecutedPrefetch as LastExecutedPrefetch
import dftpl.analyzers.windows.LastExecutedUserAssist as LastExecutedUserAssist
import dftpl.analyzers.windows.LastShutdown as LastShutdown
import dftpl.analyzers.windows.NetworkCards as NetworkCards
import dftpl.analyzers.windows.NetworkProfiles as NetworkProfiles
import dftpl.analyzers.windows.ProcessCreation as ProcessCreation
import dftpl.analyzers.windows.ProgramOpened as ProgramOpened
import dftpl.analyzers.windows.RecycleBin as RecycleBin
import dftpl.analyzers.windows.RunRunOnceRegistry as RunRunOnceRegistry
import dftpl.analyzers.windows.ServiceInstalled as ServiceInstalled
import dftpl.analyzers.windows.TimezoneSettings as TimezoneSettings
import dftpl.analyzers.windows.TrustRecordsRegistry as TrustRecordsRegistry
import dftpl.analyzers.windows.Users as Users

# DFTPL Classes
from dftpl.events.HighLevelEvent import HighLevelEvent
from dftpl.events.LowLevelEvent import LowLevelEvent

# To run DFTPL
from dftpl.reader.CSVReader import CSVReader
from dftpl.timelines.HighLevelTimeline import HighLevelTimeline, MergeHighLevelTimeline
from dftpl.timelines.LowLevelTimeline import LowLevelTimeline

# Accessing user's session values
from flask import session

# For database
from sqlalchemy import create_engine, text
from sqlalchemy.event import listen
from sqlalchemy.orm import scoped_session, sessionmaker

import app.model.timeline_model as TLModel
import app.model.fts5_model as fts5Model
from app import current_app

# Default analysers list, made a const for multiple functions
DEFAULT_analyser = {
    # FileDownloads.description: FileDownloads,
    # RecentFileAccess.description: RecentFileAccess,
    # SoftwareInstallation.description: SoftwareInstallation, # Disabled since bug in dftpl
    USBConnectedRegDeviceClasses.description: USBConnectedRegDeviceClasses,
    USBConnectedRegUSB.description: USBConnectedRegUSB,
    USBConnectedRegUSBSTOR.description: USBConnectedRegUSBSTOR,
    USBConnectedWinevt.description: USBConnectedWinevt,
    WindowsEventLogCleared.description: WindowsEventLogCleared,
    WindowsFirewallDisabled.description: WindowsFirewallDisabled,
    AllImagesFromCache.description: AllImagesFromCache,
    # AllVideoFromCache.description: AllVideoFromCache, # Disabled since bug in dftpl
    # BingSearch.description: BingSearch,
    # GoogleSearch.description: GoogleSearch,
    WebVisits.description: WebVisits,
    DefaultBrowser.description: DefaultBrowser,
    DeviceInstallation.description: DeviceInstallation,
    FailedLogin.description: FailedLogin,
    FileMRURegistry.description: FileMRURegistry,
    LastExecutedBAM.description: LastExecutedBAM,
    LastExecutedPCA.description: LastExecutedPCA,
    LastExecutedPrefetch.description: LastExecutedPrefetch,
    LastExecutedUserAssist.description: LastExecutedUserAssist,
    LastShutdown.description: LastShutdown,
    NetworkCards.description: NetworkCards,
    NetworkProfiles.description: NetworkProfiles,
    ProcessCreation.description: ProcessCreation,
    ProgramOpened.description: ProgramOpened,
    RecycleBin.description: RecycleBin,
    RunRunOnceRegistry.description: RunRunOnceRegistry,
    ServiceInstalled.description: ServiceInstalled,
    TimezoneSettings.description: TimezoneSettings,
    TrustRecordsRegistry.description: TrustRecordsRegistry,
    Users.description: Users
}


# Generate an updated analysers.json file
# Call on startup
def generate_analysers_list():
    analyser_list = {"analysers-list": []}
    # TODO: Make a template class for all analysers
    for analyser in DEFAULT_analyser.values():
        analyser_list["analysers-list"].append(
            {"name": analyser.description, "category": analyser.analyser_category}
        )
    try:
        with open(
            join(current_app.config["APP_DIR"], "dftpl_helper", "analysers.json"),
            "w",
            encoding="utf-8",
        ) as f:
            dump(analyser_list, f, ensure_ascii=False, indent=4)
    except OSError:
        # HACK: LOGGING PLS
        print("ERROR: Writing analysers.json")


# Create and store timeline data in sqlite db
# User can change the default name when they download it
# FIXME: Catch error
# HACK: Creates a session var for the loading status of dftpl
def store_timelines(low_timeline: LowLevelTimeline, high_timeline: HighLevelTimeline):
    # Create DB using model
    
    db_name = token_hex(16) + ".sqlite"
    engine = create_engine(
        (
            "sqlite:///"
            + current_app.config["UPLOAD_DIR"]
            + "\\"
            + db_name
        ),
    )

    listen(TLModel.LowLevelEvents.__table__, 'after_create', fts5Model.CreateFtsTable(TLModel.LowLevelEvents))
    listen(TLModel.HighLevelEvents.__table__, 'after_create', fts5Model.CreateFtsTable(TLModel.HighLevelEvents))

    TLModel.Base.metadata.create_all(engine)
    # Write both high level and low level timelines to db
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    listen(TLModel.LowLevelEvents, 'after_insert', fts5Model.attach_fts_low_level)
    listen(TLModel.HighLevelEvents, 'after_insert', fts5Model.attach_fts_high_level)


    # Iterate over low level events and write to DB
    count = 1
    progress_10k = 0
    for event in low_timeline.events:
         # insert every 10k entries, prevent large memory usage but keep speed shorter than individual commits
        # Since dftpl id = index = which row as ordered in the csv file,
        # "autoincrement" primary key will assign the same id
        # as dftpl.
        # Relationships will be added when adding high level events.
        db_session.add(
            TLModel.LowLevelEvents(
                # HACK: Handling '0000-00-00T00:00:00.000000+00:00' by storing raw string
                date_time_min=event.date_time_min,
                date_time_max=event.date_time_max,
                event_type=event.type,
                path=event.path,
                evidence=event.evidence,
                plugin=event.plugin,
                provenance_raw_entry=",".join(str(element) for element in event.provenance["raw_entry"]),
                keys=event.keys,
            )
        )
        count += 1
        # Commit before adding high level events and relationships
        if count >= 10000:
            progress_10k += 1
            print(f"Low level events: {progress_10k * count}")
            count = 1
            db_session.commit()
    db_session.commit() # Commit remaining
    # TEST
    print("Lowlevelevents commited")
    # Iterate over high level events and write to DB
    count = 1
    progress_10k = 0
    for event in high_timeline.events:
        # Since dftpl id = index = which row as ordered in the csv file,
        # "autoincrement" primary key will assign the same id
        # as dftpl.
        # Relationships will be added when adding high level events.
        new_event = TLModel.HighLevelEvents(
            # HACK: Handling '0000-00-00T00:00:00.000000+00:00' by storing raw string
            date_time_min=event.date_time_min,
            date_time_max=event.date_time_max,
            event_type=event.type,
            description=event.description,
            category=event.category,
            reasoning_description=event.trigger["description"],
            reasoning_reference=event.trigger["references"],
            test_event_type=event.trigger["test_event"]["type"],
            test_event_evidence=event.trigger["test_event"]["evidence"],
            # Below's code looks up the low level timeline object and assigns the relationship
            low_level_event=db_session.query(TLModel.LowLevelEvents)
            .filter(TLModel.LowLevelEvents.id == event.id)
            .first(),  # HACK: Is there a faster way?
        )

        # Key values is stored separately
        for key, value in event.keys.items():
            new_event.keys.append(
                TLModel.Keys(
                    key_name=key,
                    key_value=value,
                )
            )

        # Add Many to Many relationship values
        # HACK: Is there a faster way?
        # Below's code looks up the low level timeline object and assigns the relationship
        for event_dict in event.supporting["before"]:
            new_event.supporting_before.append(
                db_session.query(TLModel.LowLevelEvents)
                .filter(TLModel.LowLevelEvents.id == event_dict["id"])
                .first()
            )
        for event_dict in event.supporting["after"]:
            new_event.supporting_after.append(
                db_session.query(TLModel.LowLevelEvents)
                .filter(TLModel.LowLevelEvents.id == event_dict["id"])
                .first()
            )
        count += 1
        # Commit before adding high level events and relationships
        if count >= 10000:
            progress_10k += 1
            print(f"High level events: {progress_10k * count}")
            count = 1
            db_session.commit()
    # Save and close DB connection
    db_session.commit()
    print("Highlevelevents commited") # TEST
    db_session.remove()
    engine.dispose()
    # If no error, store DB Name to session
    session["session_db"] = db_name
    print("Done") # TEST
    return 0

# analysers_arr = List of names based on the analysers's description variable
# HACK: Creates a session var for the loading status of dftpl
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
            DEFAULT_analyser.get(selected)
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

    # FIXME: If no high level timelines is detected, return early
    if len(merged_high_timelines.events) < 1:
        return -1
    # Writing to database
    if store_timelines(low_timeline=low_timeline, high_timeline=merged_high_timelines) == 0:

        # Delete csv file once done
        # TODO: Split into separate function that can be imported for reusability
        if "session_csv" in session:
            remove(join(current_app.config['UPLOAD_DIR'], session.pop('session_csv', None)))
            return 0
        else:
            return -1
    else:
        return -1