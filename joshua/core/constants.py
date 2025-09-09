"""
Constants used throughout the Joshua system.

This module centralizes all constants to avoid magic numbers and strings
scattered throughout the codebase.
"""

# FoundationDB Configuration
FDB_API_VERSION = 630
ONE = b"\x01" + b"\x00" * 7  # Used for atomic increments

# Blob Storage Limits
BLOB_KEY_LIMIT = 8192  # Maximum size for a single key in FDB
BLOB_TRANSACTION_LIMIT = 128 * 1024  # Maximum transaction size

# Time Formats
TIMESTAMP_FMT = "%Y%m%d-%H%M%S"
DATE_FORMAT = "%Y-%b-%d (%a) %I:%M:%S %p"

# Default Values
DEFAULT_TIMEOUT = 5400  # 90 minutes in seconds
DEFAULT_FAIL_FAST = 10  # Stop after 10 failures
DEFAULT_MAX_RUNS = 100000  # Maximum runs per ensemble
DEFAULT_PRIORITY = 100  # Default priority percentage

# Agent Configuration
AGENT_HEARTBEAT_INTERVAL = 1.0  # Seconds between heartbeats
AGENT_DEATH_THRESHOLD = 10  # Seconds before agent is presumed dead
AGENT_DEFAULT_WORK_DIR = "/tmp/joshua_agent"

# Environment Variables
ENV_JOSHUA_USER = "JOSHUA_USER"
ENV_JOSHUA_NAMESPACE = "JOSHUA_NAMESPACE"
ENV_JOSHUA_MARKER = "OF_HOUSE_JOSHUA"  # Marker for child processes
ENV_INSTANCE_ID = "PLATFORM_SHORT_INSTANCE_ID"
ENV_OLD_INSTANCE_ID = "SHORT_TASK_ID"
ENV_HOSTNAME = "HOSTNAME"
ENV_CLUSTER_FILE = "FDB_CLUSTER_FILE"
ENV_AGENT_STOPFILE = "AGENT_STOPFILE"

# Kubernetes Configuration
K8S_NAMESPACE_FILE = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
K8S_LABEL_ENSEMBLE = "ensemble"
K8S_LABEL_LAST_TEST = "last_test"
K8S_MAX_LABEL_LENGTH = 63  # Kubernetes label length limit

# File Names
JOSHUA_TEST_SCRIPT = "joshua_test"
JOSHUA_DONE_SCRIPT = "joshua_done"
JOSHUA_TIMEOUT_SCRIPT = "joshua_timeout"

# Directory Names
DIR_ENSEMBLES = "ensembles"
DIR_GLOBAL_DATA = "global_data"
DIR_TMP = "tmp"
DIR_RUNS = "runs"

# Result Codes
RESULT_SUCCESS = 0
RESULT_FAILURE = 1
RESULT_CANCELLED = -1
RESULT_TIMEOUT = -2
RESULT_STOPPED = -3

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
LOG_FILE = "/tmp/joshua.log"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# Artifacts
ARTIFACT_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds
ARTIFACT_SAVE_ALWAYS = "ALWAYS"
ARTIFACT_SAVE_FAILURE = "FAILURE"
ARTIFACT_SAVE_NEVER = "NEVER"

# Process Management
PROCESS_KILL_ATTEMPTS = 10
PROCESS_WAIT_TIMEOUT = 5  # Seconds to wait for process death
ZOMBIE_CHECK_PATTERN = "<defunct>"

# Tarball Validation
MAX_TARBALL_SIZE = 100 * 1024 * 1024  # 100MB
UNSAFE_PATH_PATTERNS = ['..', '/']

# XML Message Tags
XML_TEST_TAG = "Test"
XML_ERROR_TAG = "JoshuaError"
XML_MESSAGE_TAG = "JoshuaMessage"
XML_SEVERITY_ERROR = "40"
XML_SEVERITY_INFO = "10"