# Galaxy Buds Pro Headtracking
Stream head-tracking data from the Samsung Galaxy Buds Pro in real-time

## Requirements

### Windows

On Windows, make sure to install version 0.22 of PyBluez.
The latest version (v0.23) does not work properly and fails to enumerate Bluetooth devices.
```
pip install PyBluez==0.22
```

### Linux

On Linux, you can just go ahead and install the latest version of PyBluez.
```
pip install PyBluez
```

## Usage
```
python Headtracking.py --help
```
```
usage: Headtracking.py [-h] [-v] [-t] mac-address

Stream head-tracking data from the Galaxy Buds Pro

positional arguments:
  mac-address    MAC-Address of your Buds

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Print debug information
  -t, --trace    Trace Bluetooth serial traffic

```
Dump raw head-tracking data as a quaternion (4D vector):
```
python Headtracking.py 64:03:7f:2e:2b:3a
```
```
x=0.0159, y=0.0096, z=0.0134, w=0.0245
x=0.0179, y=0.0171, z=0.0127, w=0.0251
x=0.0178, y=0.0172, z=0.0146, w=0.0000
x=0.0168, y=0.0103, z=0.0056, w=0.0226
x=0.0165, y=0.0123, z=0.0149, w=0.0252
x=0.0164, y=0.0122, z=0.0151, w=0.0252
x=0.0153, y=0.0085, z=0.0181, w=0.0000
x=0.0172, y=0.0162, z=0.0178, w=0.0006
x=0.0170, y=0.0156, z=0.0182, w=0.0007
x=0.0177, y=0.0167, z=0.0141, w=0.0255
x=0.0164, y=0.0120, z=0.0148, w=0.0252
x=0.0167, y=0.0143, z=0.0182, w=0.0006
```
