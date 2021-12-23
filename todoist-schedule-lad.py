# Set up logging
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simpleExample')
logger.info('Started processing...')

# Import dependencies
import argparse # Used to parse command line arguments
import yaml # Used to parse config file
import re # Regex used to extract project date from project name, also to validate and parse labels eg. +1w
from datetime import datetime, timedelta
from todoist.api import TodoistAPI

# Initialise variables
regex_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
regex_label_name = re.compile(r"^([-\+])(\d+)([dw])$")
any_changes = False

# Parse API key file
config_file = open('apikey.yaml', 'r')
config = yaml.safe_load(config_file)
logger.debug(config)
api_key = config['ApiKey']

# Parse arguments from command line
logger.info('Parsing arguments from command line...')
parser = argparse.ArgumentParser(description='Update the scheduled dates of tasks in a specified Todoist project, based on a date obtained in YYYY-MM-DD format from the project name, or specified when running the program.')
parser.add_argument('p', type=int, help='Project ID (integer)')
parser.add_argument('-d', help='Project date (YYYY-MM-DD)')
args = parser.parse_args()
logging.debug(args)

project_id = args.p;
project_date = args.d;

# Check that the format of the variables/parameters is as expected
assert api_key is not None and api_key != ''
assert project_id is not None and project_id != ''
assert project_date is None or regex_date.match(project_date)

# Perform initial sync
logging.info('Connecting and synchronising...')
api = TodoistAPI(api_key)
api.sync()

# Cache "date offset" labels in a new dictionary
logging.info('Caching labels if their name matches the pattern (eg. -1w)')
label_names = dict()
for label in api.state['labels']:
	if regex_label_name.match(label['name']):
		label_names[label['id']] = label['name']
		logging.debug('Cached label %s (%s)', label['id'], label['name'])
	else:
		logging.debug('Discarded label %s (%s)', label['id'], label['name'])

# Get project data, including items in project
project = api.projects.get_data(project_id)
logging.info('Retrieved project %s (%s)' , project['project']['id'] , project['project']['name'])

# If project_date is not set, try to find the project date in the project name
if project_date is None:
	logging.info('Project date was not provided as a parameter.')
	if regex_date.match(project['project']['name']):
		logging.info('Extracting project date from project name...')
		regex_date_matches = regex_date.findall(project['project']['name'])
		project_date = str(regex_date_matches[0][0]) + '-' + str(regex_date_matches[0][1]) + '-' + str(regex_date_matches[0][2])
	else:
		raise ValueError('Project date could not be found in the project name.')
	assert regex_date.match(project_date)

# We should now have a project and a valid project date
project_date = datetime.strptime(project_date, '%Y-%m-%d')
if type(project_date) is not datetime:
	raise TypeError('Project_date must be a datetime.date, not a %s' % type(project_date))
logging.info('Project base date is %s', project_date)

# For each project, for each item (task), check for "date offset" labels (eg. -3w)
for item in project['items']:
	logging.info('Processing item %s (%s)', item['id'], item['content'])
	if len(item['labels']) == 0:
		logging.debug('No labels')
	for label in item['labels']:
		if label not in label_names:
			logging.debug('Ignoring label %s', label)
		else:
			# Process label
			label_name = label_names[label]
			logging.debug('Processing label %s (%s)', label, label_name)
			# Calculate new schedule date relative to the project date
			offset = re.findall(regex_label_name, label_name)
			offset_operator = offset[0][0]
			offset_value = int(offset[0][1])
			offset_unit = offset[0][2]
			logging.debug('Required offset is %s%s%s', offset_operator, offset_value, offset_unit)
			if offset_unit == 'w':
				offset_days = offset_value * 7
			else:
				offset_days = offset_value
			if offset_operator == '-':
				item_date = project_date - timedelta(days=offset_days)
			else:
				item_date = project_date + timedelta(days=offset_days)
			logging.debug('Offset date is %s', item_date.strftime("%Y-%m-%d"))
			# Only reschedule item if needed
			if item['due'] is None:
				logging.info('Schedule at %s%s%s which is %s', offset_operator, offset_value, offset_unit, item_date.strftime("%Y-%m-%d"))
				item2 = api.items.get_by_id(item['id'])
				item2.update(due={'date': item_date.strftime("%Y-%m-%d")})
				any_changes = True
			elif item_date.strftime("%Y-%m-%d") != item['due']['date']:
				logging.info('Reschedule from %s by %s%s%s to %s', item['due']['date'], offset_operator, offset_value, offset_unit, item_date.strftime("%Y-%m-%d"))
				item2 = api.items.get_by_id(item['id'])
				item2.update(due={'date': item_date.strftime("%Y-%m-%d")})
				any_changes = True
			else:
				logging.info('Already offset by %s%s%s (%s)', offset_operator, offset_value, offset_unit, item['due']['date'])

if any_changes:
	logging.info('Committing changes...')
	commit = api.commit()
	logging.debug(commit)

logger.info('Finished processing.')