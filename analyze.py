import sqlite3, datetime, jinja2, os, json, time, shutil, sys

### copy txt file here
#sys.exec('''
#	cd ~/Library/Application\ Support/MobileSync/Backup/;
#	if [ -e $(ls -t | head -n 1)/3d0d7e5fb2ce288813306e4d4636395e047a3d28 ]; then
#		cp 3d0d7e5fb2ce288813306e4d4636395e047a3d28 '%s/txts.sqlite'
#	fi
#	''' % (os.path.dirname(os.path.abspath(__file__))))

#os.path.isfile(fname)


def copy_file():
  old_wdir = os.getcwd()
  backup_dir = os.path.join(os.path.expanduser('~'), 'Library/Application Support/MobileSync/Backup/')
  os.chdir(backup_dir)
  all_subdirs = [d for d in os.listdir('./') if os.path.isdir(d)]
  latest_subdir = max(all_subdirs, key=os.path.getmtime)
  txt_backup = os.path.join(backup_dir, latest_subdir,'3d0d7e5fb2ce288813306e4d4636395e047a3d28')
  if (os.path.isfile(txt_backup)):
    print('Found database - Copying.')
    os.chdir(old_wdir)
    db_file = './data/txts-'+str(int(os.path.getmtime(txt_backup)))+'.sqlite'
    shutil.copyfile(txt_backup, os.path.join(os.path.dirname(__file__), db_file))
    return db_file
  else:
    print('DB File not found for copying!')
    os.chdir(old_wdir)

db_file = copy_file()

print('Opening database')

## open txt file in sqlite
conn = sqlite3.connect(db_file)

## then generate json, for webpage.

# find first date
c = conn.cursor()

c.execute('SELECT date FROM message limit 1')
start_date = datetime.datetime.fromtimestamp(int(c.fetchone()[0]))
# and last date
c.execute('SELECT date FROM message ORDER BY rowid DESC LIMIT 1;')
end_date = datetime.datetime.fromtimestamp(int(c.fetchone()[0]))
# find last date

def to_num(date_in):
  return int(date_in.strftime('%s'))

def add_months(date_in, num_chg = 1):
  month = date_in.month - 1 + num_chg
  year = date_in.year + int(month / 12)
  month = month % 12 + 1
  return datetime.datetime(year, month, 1)

cur_date = datetime.datetime(start_date.year, start_date.month, 1)

updates = []

imessage_offset = 978307200

end_date = datetime.datetime.now()
while (end_date > cur_date):
  fetch_start = cur_date
  cur_date = add_months(cur_date)
  c.execute('SELECT COUNT(*) FROM message WHERE (date < %i and date > %i) or (date < %i and date > %i)' %
  	 (to_num(cur_date), to_num(fetch_start), to_num(cur_date) - imessage_offset, to_num(fetch_start) - imessage_offset))
  record = c.fetchone()[0]
  updates.append((cur_date, record))


## fire up jinja2.

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

tpl = env.get_template('main.html')

## generate some json

dthandler = lambda obj: int(time.mktime(obj.timetuple())) if isinstance(obj, datetime.datetime) else None
result = tpl.render({'updates': json.dumps(updates, default=dthandler)})


## output txt msg analysis webpage, embed scripts

with open('output.html', 'w') as f:
  f.write(result)

## Write the result -- Profit?!? $$$
