# DB Purging Py
A simple python script for database purging.

## Scenario
You have 2 tables:

- Main Table
- Backup Table

Your main service like let's say transactions hit the main table for data and backup table is for reconciliation or audit purposes.

Backup table will persist data of D-1 till D-29 means 1 months of data in backup table. If your daily transaction is really very high, for our case 8 Million rows. Hence, you can not just move the rows by date to backup table. There is a high chance:

- Table will get locked
- Memory usage will go high
- Other databases in the same host will get impacted

Yes, you heard it right. We faced all the scenario while our old script tried to purge data. Old script was made when there were very less transactions and it was working fine by the way till transactions reached high.

## Why Purging is required
As you are aware that if a table data grows, query and insertion becomes slower. Which impacts

- Performance
- Application RTT
- Sudden hiccups

## Packages
I have used the following packages of python to build

- pymysql
- datetime
- time

## Configure
Add the required parameters in the configuration, and you are ready to run the script. Here is an example of my case.

```init
[database]
ip=127.0.0.1
port=3306
name=purchase
user=root
pass=toor

[main_table]
table_name=transactions
table_time_field_name=updated_at
table_order_by=updated_at
table_id_column=id
table_purge_chunk=10000 # Select 10K rows each time
table_before_minutes=300 # Before 5 Minutes

[backup_table]
table_name=transactions_backup
table_time_field_name=updated_at
table_order_by=updated_at
table_id_column=id
table_purge_chunk=100000 # Select 100K rows each time
table_purge_days=30 # 30 Days of data to keep in backup
```

## Run from CRON
For running the script and logging the flow

```bash
*/10 * * * * python <location>/main.py 2&>1 <location>/purge.log
```
Means it will run every 10 minutes and put the logs in a file named `purge.log` file. Later you can check the log file for time information.

## Suggestions
Please do mail me for any suggestions, I will be glad to include [ferdousul.haque@gmail.com](ferdousul.haque@gmail.com)

## Install the required packages
Run the following command to run the virtual environment for python and install packages for run

```bash
./venv/Scripts/activate
pip install -r requirements.txt
python main.py
```