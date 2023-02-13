#!/usr/bin/env python

import os
import subprocess

from doodbalib import logger

DB_SOURCE = os.environ.get("PGDATABASE", "odoo")
BACKUP_LOCATION = os.environ.get("BACKUP_LOCATION", "odoo")

PGUSER = os.environ.get("PGUSER", "odoo")
PGPASSWORD = os.environ.get("PGPASSWORD")

if os.environ.get("RESTORE_BACKUP"):
    logger.info("Setup the PostgreSQL credentials file.")
    path = "%s/.pgpass" % os.path.expanduser("~")
    with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), "w") as fh:
        fh.writelines(["db:5432:%s:%s:%s" % (DB_SOURCE, PGUSER, PGPASSWORD)])

    logger.info("Restore the database backup into the source database.")
    try:
        logger.debug(subprocess.check_output(["dropdb", "-h", "db", DB_SOURCE]))
    except subprocess.CalledProcessError as e:
        logger.debug(e.output)
    logger.debug(subprocess.check_output(["createdb", "-h", "db", DB_SOURCE]))
    logger.debug(
        subprocess.check_output(
            'psql -h db -d "%s" < %s/dump.sql'
            % (
                DB_SOURCE,
                BACKUP_LOCATION,
            ),
            shell=True,
        )
    )

    logger.info("Copying filestore to the volume.")
    logger.info(
        subprocess.check_output(
            ["rm", "-rf", "%s/filestore/%s" % ("/var/lib/odoo", DB_SOURCE)]
        )
    )
    logger.info(
        subprocess.check_output(
            ["mkdir", "-p", "%s/filestore/%s" % ("/var/lib/odoo", DB_SOURCE)]
        )
    )
    logger.debug(
        subprocess.check_output(
            [
                "cp",
                "-rf",
                "%s/filestore" % (BACKUP_LOCATION),
                "%s/filestore/%s" % ("/var/lib/odoo", DB_SOURCE),
            ]
        )
    )
