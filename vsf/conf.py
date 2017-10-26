from vsf import settings

# Variables for formula:

# X1 repeated soft flags for the same ISP,
# same target and same type (DNS, TCP, HTTP..)
# in the last Y1 reports

SOFT_FLAG_REPEATED_X1 = 3
LAST_REPORTS_Y1 = 10
FLAGS_TIME_WINDOW = 30  # days

# Variables for formula:

# X2 repeated soft flags for the same ISP,
# same target, same type (DNS, TCP, HTTP..),
# and same region in the last Y2 reports

SOFT_FLAG_REPEATED_X2 = 2
LAST_REPORTS_Y2 = 10
