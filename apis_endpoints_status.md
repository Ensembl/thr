## APIs Endpoints Status

##### Regitration API (RESTful workflow)

| Endpoint name                   | Description                                                | Status      |
| ------------------------------- | ---------------------------------------------------------- | ----------- |
| POST /api/user                  | Get information about the current user                     | Done        |
| POST /api/user/register         | Register a new user and obtain the access token            | Done        |
| POST /api/user/login            | Login and get the authentication token                     | Done        |
| POST /api/user/logout           | Logout and invalidate the current access token             | Done        |
| GET /api/trackhub               | Returns the set of registered track data hubs for the given user| Done   |
| GET /api/trackhub/:id           | Return a track hub with the given name in the Registry     | Done        |
| DELETE /api/trackhub/:id        | Delete trackDBs assigned to a given track hub              | Done        |
| GET /api/trackdb/:id            | Return the trackDb with the given ID in the Registry       | Todo        |
| POST /api/trackhub              | Register/Update a remote public track hub with the Registry| Done        |
| DELETE /api/trackdb/:id         | Delete the trackDb with the given ID from the Registry     | Todo        |


##### Info APIs

| Endpoint name                              | Description                                                | Status      |
| ------------------------------------------ | ---------------------------------------------------------- | ----------- |
| GET /api/info/version                      | Returns the current version of all the Registry APIs       | Todo        |
| GET /api/info/ping	                     | Checks if the service is alive                             | Todo        |
| GET /api/info/species	                     | Returns the set of species the track hubs registered in the Registry contain data for| Todo       |
| GET /api/info/assemblies	                 | Returns the set of assemblies the track hubs registered in the Registry contain data for| Todo    |
| GET /api/info/hubs_per_assembly/:assembly  | Returns the number of hubs for a given assembly, specified either by INSDC name or accession| Todo|
| GET /api/info/tracks_per_assembly/:assembly| Returns the number of tracks for a given assembly, specified by INSDC name or accession     | Todo|
| GET /api/v1/info/trackhubs                 | Return the list of registered track data hubs              | Todo        |

##### Search API

| Endpoint name                     | Description                                                    | Status      |
| --------------------------------- | -------------------------------------------------------------- | ----------- |
| POST /api/search                  | Search track hubs using a query specified in the message body  | Todo        |
| GET /api/search/trackdb/:id       | Returns data suitable to be displayed in the main page as a brief summary of the content of the data| Todo|
| POST /api/search/biosample        | Support querying by list of BioSample IDs                      | ????        |
| GET/api/search/all                | Used by trackfind to mine the Trackhub Registry for metadata   | ????        |

##### Stats API

| Endpoint name                | Description                                                                                                      | Status      |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------- | ----------- |
| GET /api/v1/stats/complete   | Returns complete data with which to build various stats based on species/assembly/file type on a dedicated page  | Todo        |
| GET /api/v1/stats/summary    | Returns data suitable to be displayed in the main page as a brief summary of the content of the data             | Todo        |
