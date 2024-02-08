
CREATE USER dispo PASSWORD 'mysecretpassword';
CREATE DATABASE dispo;
GRANT ALL PRIVILEGES ON DATABASE dispo TO dispo;
GRANT CREATE ON DATABASE dispo to dispo;
ALTER DATABASE dispo OWNER TO dispo;

CREATE USER cleaning PASSWORD 'mysecretpassword';
CREATE DATABASE cleaning;
GRANT ALL PRIVILEGES ON DATABASE cleaning TO cleaning;
GRANT CREATE ON DATABASE cleaning to cleaning;
ALTER DATABASE cleaning OWNER TO cleaning;


