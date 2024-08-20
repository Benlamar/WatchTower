# WatchTower


## Prerequisites
Python 3.8 or higher
Node.js and npm (for the React frontend)
Redis server
SQLite/MySQL/PostgreSQL
Celery
Flower (Optional)

## Notes
Ensure Redis is installed and running before starting the Celery worker. You can download Redis from here.

## Setup and Running
You can create a virtual environment install the requirements.
 

### Start the Celery Worker
On a terminal, start the fastapi server :
```uvicorn main:app --reload ```
you can use your own port using ```--port=8008```

### Start the Celery Worker
In a different terminal, start celery with the following :
```celery -A service.Tasker.c_tasker worker --loglevel=info -P solo```
for Debian ```-P solo``` is not requiered



