# SAP to Irail Integration Tool

## Introduction

This project is designed to create a bridge between SAP systems and the Irail system used by Israel Rail for GIS purposes. The primary goal is to allow the SAP system to send requests to a SOAP service, part of the backend of the Irail system. Based on the parameters provided by the user, this service executes the necessary operations.

## Features

### Four Types of Operations
The tool supports four distinct operations, each catering to different GIS needs:
1. **Point Event with Latitude and Longitude:** Specify the exact coordinates.
2. **Center of Geometry:** Generates a point based on the center of a queried geometry.
3. **Polyline Shape:** Create a polyline shape using 'from' and 'to' km parameters, along with 'tplnr.'
4. **Point Event with 'tplnr' and 'km':** Generate a point event using specific parameters.

## Implementation

The tool is built as a toolbox in ArcMap and utilizes the ArcPy library. It operates by adding entries to layers on the map in different variations. These events correspond to entries in an attribute table of a layer in an MXD published to ARSI's portal version 10.6.

## Usage

**Note:** Detailed usage instructions will depend on your specific implementation and should be included here to guide users on how to operate the tool.

## Contributing

Feel free to contribute to the project by opening issues or submitting pull requests.

## License

Include information about the license under which the project is released, if applicable.

