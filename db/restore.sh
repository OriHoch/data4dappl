rm -rf /var/lib/postgresql/data/*;
docker-entrypoint.sh postgres &
while ! su postgres -c "pg_isready"; do
    echo waiting for DB to accept connections...
    sleep 1
done
while ! [ -e "${BACKUP_DATABASE_FILE}" ]; do
    echo waiting for backup file "${BACKUP_DATABASE_FILE}"
    sleep 1
done
echo sleeping 5 seconds to let DB start properly
sleep 5
! su postgres -c "psql -c 'create database ckan;'" && echo Failed to create ckan database && exit 1
! su postgres -c "psql -d ckan -c \"create role ckan with login password '${POSTGRES_PASSWORD}';\"" && echo failed to create ckan role && exit 1
! su postgres -c "pg_restore --exit-on-error -d ${BACKUP_DATABASE_NAME} ${BACKUP_DATABASE_FILE}" > /dev/null \
    && echo failed to restore from backup && exit 1
! su postgres -c "psql -d ckan -c 'grant all privileges on database ckan to ckan;'" && echo failed to grant privileges to ckan role && exit 1
! su postgres -c "psql -d ckan -c 'grant all privileges on all tables in schema public to ckan;'" && echo failed to grant privileges to ckan role && exit 1
echo Successfully restored from backup, continuing to serve the DB
wait
