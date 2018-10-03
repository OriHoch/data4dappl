rm -rf /var/lib/postgresql/data/*;
docker-entrypoint.sh postgres &
while ! su postgres -c "pg_isready"; do
  echo waiting for DB to accept connections...
  sleep 1
done
sleep 2
! su postgres -c "createdb ckan -E utf-8" && echo failed to create ckan db && exit 1
! su postgres -c "psql -c \"create role ckan with login password '${POSTGRES_PASSWORD}';\"" && echo failed to create ckan role && exit 1
! su postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE \"ckan\" to ckan;'" && echo failed to grant privileges to ckan role && exit 1
echo Successfully initialized the DB, continuing to serve the DB
wait
