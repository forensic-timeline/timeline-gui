# Functions to run DFTPL. Based on "dftpl.py" branch "python-analyzers" (as of 03052025)
from app import current_app
from app.model.timeline_model import SCHEMA_TABLE_SQL_VAL


from dftpl.reader.CSVReader import CSVReader
from dftpl.timelines.LowLevelTimeline import LowLevelTimeline
from dftpl.timelines.HighLevelTimeline import MergeHighLevelTimeline
# Import all dftpl analyzers by default
# Update the list of usable analyzers to match dftpl
# TEST: Only imported analyzers needed for testing
# TODO: Add a function in dftpl to generate:
# 1. dictionary mapping of all analyzer classes
# 2. update analyzers.json list of all analyzers
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

# Default analyzers list, made a const for multiple functions
DEFAULT_ANALYZERS = {
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
    ProgramOpened.description: ProgramOpened
}
# Generate an updated analyzers.json file
# Call on startup

# Create and store timeline data in sqlite db
# User can change the default name when they download it
def store_timelines(low_timeline, high_timeline)
    # Create DB using model

    # Write both high level and low level timelines to db

    # Save and close DB connection

def run_dftpl(input_file_path, analyzers_arr):
        # Read the CSV file
    print('Reading CSV file ...')
    reader = CSVReader(input_file_path)

    # Create a list of LowLevelEvent objects
    print('Creating low-level timeline ...')
    low_timeline = LowLevelTimeline()
    low_timeline.create_timeline(reader)

    # Create a list of high-level timeline
    high_timelines = []

    # Get list of search analyzers selected by users, if empty default to all
    selected_analyzers = []
    for selected in analyzers_arr:
        selected_analyzers.append(DEFAULT_ANALYZERS.get(selected, DEFAULT_ANALYZERS.values))

    # Run each search analyzer
    for analyzer in selected_analyzers:
        print(f'Running {analyzer.description} analyzer ...')
        high_timeline = analyzer.Run(low_timeline)
        if high_timeline:
            high_timelines.append(high_timeline)

    # Merge the high-level timelines
    print('Merging high-level timelines ...')
    merge_timelines = MergeHighLevelTimeline(high_timelines)
    merged_high_timelines = merge_timelines.merge()

