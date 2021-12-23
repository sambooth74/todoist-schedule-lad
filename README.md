# todoist-schedule-lad
Schedule Todoist tasks by label and date

This script schedules Todoist tasks in a specified Todoist project to a new date, calculated using a label and a project date.

* The project ID must be provided as a command-line parameter.
* The project date is obtained in YYYY-MM-DD format from the project name, or can optionally be provided as a command-line parameter.
* The label is in the format eg. -3w, representing minus 3 weeks.

_I'm a novice coder, so please help improve this script if you can._

## Example usage

`python todoist-schedule-lad.py 2265853802`

This example will schedule tasks in project 2265853802 relative to a date found in the project name (YYYY-MM-DD format).

If the project name was "2021-11-05: Bonfire Night" then the tasks would be scheduled relative to 5 November 2021.

`python todoist-schedule-lad.py 2265853802 01-01-2022`

This example will schedule tasks in project 2265853802 relative to the date 1 January 2022, and ignore any date provided in the project name.

## Requirements

You will need to obtain your own Todoist API key. Copy and paste this key into `apikey.conf` (see `apikey_template.conf` for the correct format)
