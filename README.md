# soundscape-zero

A tile server for [Microsoft Soundscape](https://github.com/microsoft/soundscape/)
with no bulk data processing or storage footprint.

The released Soundscape server code required terabytes of storage and cloud
resources to build its own OpenStreeMap database. soundscape-zero accepts the
same API requests, but translates them into
[Overpass QL](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL)
queries that are executed on a standard
[Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API) server.

This will hopefully allow the app to better leverage existing public
infrastructure, and consequently reduce the burden of operating it.
