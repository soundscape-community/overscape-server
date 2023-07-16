# Overscape

Overscape is a replacement for some of the backend services for the [Microsoft Soundscape](https://github.com/microsoft/soundscape/) iOS app.

It serves map data by sending queries to a public or privately-hosted [Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API) server. Since it doesn't store its own data, it should be simpler to deploy and run than the server code provided by Microsoft.

## Using with Soundscape app in a simulator

1. In this repository, run the server:
    1. To use a public Overpass server as the data source, run:
    ```
    $ docker build -t overscape .
    $ docker run -it --rm -p 8080:8080 overscape
    ```
    2. Alternatively, to create a local Overpass container with a small dataset (Washington, DC):
    ```
    $ docker-compose up --build
    ```
    3. To confirm the server is up and serving JSON data, use a browser to visit a tile URL like http://localhost:8080/tiles/16/18745/25070.json
2. In the Soundscape repository, in source code file [apps/ios/GuideDogs/Code/Data/Services/Helpers/ServiceModel.swift at line 36](https://github.com/microsoft/soundscape/blob/main/apps/ios/GuideDogs/Code/Data/Services/Helpers/ServiceModel.swift#L36), set the `productionServicesHostName` value to `http://localhost:8080`.
3. Open apps/ios/GuideDogs.xcworkspace in Xcode, and run the iOS simulator.
    1. To trigger queries to our local server, set "Location" (under the "Feature" menu) to a value that simulates moving, like "City Run."
    2. You may also need to install a text-to-speech voice in the iOS settings.

## Running the original Soundscape server

You can also run the original Soundscape server code as provided by Microsoft. Unlike Overscape, the Microsoft version involves loading and hosting of bulk OpenStreetMap data in a PostGIS database. See the [docker-compose file ](https://github.com/openscape-community/openscape/blob/master/svcs/data/docker-compose.yml) for details on spinning up the necessary services.

## Running tests
```
pip install -r requirements_test.txt
cd app && pytest --asyncio-mode=auto tests.py
```
