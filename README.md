# Overscape

Overscape is a replacement for some of the backend services for the [Microsoft Soundscape](https://github.com/microsoft/soundscape/) iOS app.

It serves map data by sending queries to a public or privately-hosted [Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API) server. Since it doesn't store its own data, it should be easier to deploy and run than the released server code.

## Using with Soundscape app in a simulator

1. Run the server:
```
$ docker build -t overscape .
$ docker run -it --rm -p 8080:8080 overscape
```
2. In the source code file [apps/ios/GuideDogs/Code/Data/Services/Helpers/ServiceModel.swift at line 36](https://github.com/microsoft/soundscape/blob/main/apps/ios/GuideDogs/Code/Data/Services/Helpers/ServiceModel.swift#L36), set the `productionServicesHostName` value to `http://localhost:8080.
3. Run the iPhone simulator in Xcode.
    1. Make sure to set "Location" (under the "Feature" menu) to a value like "City Run."
    2. You may also need to install a text-to-speech voice in the iOS settings.

## Running the original Soundscape server

The original server code provided by Microsoft involved loading and hosting of bulk map data, but as released was incomplete. However, I have put together a [docker-compose file](https://github.com/steinbro/soundscape/blob/docker-compose/svcs/data/docker-compose.yml) that can spin up the necessary services, if you are interested in running that instead.
