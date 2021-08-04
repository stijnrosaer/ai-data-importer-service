# ai-data-importer-service

A docker container to load data from a `triplestore` or `csv` and convert it to `json` for easy use in AI algorithms.

## Info

The data inporter service handles the loading and converting of data in both csv as SPARQL format. Depending on the
data-source, the data is converted to a uniform datastructures that is easily usable for AI algorithms. If the source is
a csv file, the file is loaded and parsed. In the case of a SPARQL query, the query is executed on a triple store after
which the data is converted to the same format.

## Getting started
```yml
services:
  ai-data-importer:
    image: redpencil/ai-data-importer
    links:
      - db:database
    environment:
      LOG_LEVEL: "debug"
      MODE: "production"
      ACCEPT_FILENAME: "true"
      ACCEPT_OPTIONS: "true"
      MU_SPARQL_ENDPOINT: "https://dbpedia.org/sparql/"
      MU_SPARQL_UPDATEPOINT: "http://database:8890/sparql"
    volumes:
      - ./config/dataconvert:/config
      - ./share:/share
```

## Reference
### Environment variables

- `ACCEPT_FILENAME` if true, the user of the endpoints provided by this service are allowed to submit a filename as
  argument. If false, a default filename is used and submitted filenames are ignored.


- `ACCEPT_OPTIONS` if true, the user of the endpoints provided by this service are allowed to submit a specific options
  as argument. If false, a default settings is used and submitted options are ignored.


- `LOG_LEVEL` takes the same options as defined in the
  Python [logging](https://docs.python.org/3/library/logging.html#logging-levels) module.


- `MU_SPARQL_ENDPOINT` is used to configure the SPARQL query endpoint.

    - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should
      be linked to the microservice container as `database`.
      

- `MU_SPARQL_UPDATEPOINT` is used to configure the SPARQL update endpoint.

    - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should
      be linked to the microservice container as `database`.


- `MU_APPLICATION_GRAPH` specifies the graph in the triple store the microservice will work in.

    - By default this is set to `http://mu.semte.ch/application`. The graph name can be used in the service
      via `settings.graph`.


- `MU_SPARQL_TIMEOUT` is used to configure the timeout (in seconds) for SPARQL queries.

### File locations

SPARQL files should be located in [config/dataconvert/](config/dataconvert/)

csv files should be located in [share/](share/)

### Endpoints

#### `GET /data/query`: load data from a query

Arguments:

- filename: filename of file housing the SPARQL query, default `input.sparql`
- limit: Number of items to be fetched from triple store per request, default `1000`
- global_limit: Total amount of items to be fetched, default `all`

#### `GET /data/file`: load data from a csv file

Arguments:

- filename: filename of the csv file, default `input.csv`
- columns: columns that should be selected and used, default `all`