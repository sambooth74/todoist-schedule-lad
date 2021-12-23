# todoist-schedule-lad
Schedule Todoist tasks by label and date

This script schedules Todoist tasks in a specified Todoist project to a new date, calculated using a label and a project date.

* The project ID must be provided as a command-line parameter.
* The project date is obtained in YYYY-MM-DD format from the project name, or can optionally be provided as a command-line parameter.
* The label is in the format eg. -3w, representing minus 3 weeks.

_I'm a novice coder, so please help improve this script if you can._

## Worked example

I have a project called "2021-11-05: Bonfire Night". The project ID number is 1122334455.

Inside are 4 tasks:

* Collect wood (label -1w)
* Build bonfire (label -1d)
* Light bonfire (+0d)
* Clean up (+1d)

I run the script using the following command line...

`python todoist-schedule-lad.py 1122334455`

The script checks the project name for a date in YYYY-MM-DD format and finds that the "project date" is 5 November 2021.

The script calculates the date offsets for each task and schedules them as follows:

* Collect wood (minus 1 week) 30 October 2021
* Build bonfire (minus 1 day) 4 November 2021
* Light bonfire (plus 0 days ie. on the day) 5 November 2021
* Clean up (plus 1 day) 6 November 2021

## Setup

You will need to obtain your own Todoist API key. Copy and paste this key into `apikey.conf` (see `apikey_template.conf` for the correct format)

## Project ID numbers

To find your project ID number, access your project in the web app and it will be at the end of the URL.

eg. `https://todoist.com/app/project/2265853802`

## Labels

The first character must be a `+` or `-`
The last character must be a `d` (for days) or `w` (for weeks)
The middle characters must be digits.

The label format is defined as a regular expression in the `regex_label_name` variable.
