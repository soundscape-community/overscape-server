# overscape

Overscape is a lightweight tile server for the
[Microsoft Soundscape](https://github.com/microsoft/soundscape/) iOS app.
Its goal is to require no bulk data processing or storage footprint.
It does so by passing queries to a standard
[Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API) server.

When Soundscape was supported by Microsoft, it relied on customize services
based on OpenStreetMap data. Now that Soundscape is an open source offering,
it can be useful to run the app against public resources, or to spin up a
personal instance. This lets individuals interested on working on the iOS
app avoid needing to deploy their own cloud services.

To run:
```
$ docker build -t overscape .
$ docker run -it --rm -p 8080:8080 overscape
```