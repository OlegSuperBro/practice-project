# Vacations-db

It's my pratice task

## How to run it

### Installing

- Download [PostgreSQL](https://www.postgresql.org/download/)
- Create [Database](#creating-database)
- Install all requirements by running ```pip install -r requerements.txt```

### Creating database

If any of that commands don't work, you should open cmd in *postgre_installation_folder/bin*

By default it's ***C:\Program Files\PostgreSQL\"your version"\bin***

1. Run ```createdb.exe -U postgres vacations```. It will ask you for password you set when [installing](#installing) postgre, after that database will be created
2. Run ```psql.exe -U postgres```. It asks your password again, but now you using psql where you can run SQL commands
3. Run ```\i "path/to/createdb.sql"```. Make sure in path you using "/" not "\\"
4. Now you can exit psql tool by typing ```\q```

### Actually running it

Just run main.py
