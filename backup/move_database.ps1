java -DMB_DB_TYPE=mysql -DMB_DB_CONNECTION_URI="jdbc:mysql://<host>:3306/metabase?user=<username>&password=<password>" -jar metabase.jar load-from-h2 metabase.db
