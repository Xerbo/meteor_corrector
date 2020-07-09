# Meteor-M2 Geometry Corrector

`meteor_corrector` is a tool for correcting the warp at the edges of images from Meteor-M2 satellite (and alike) written in python3.

It uses OpenCV for image transforms meaning that it can typically process an image in under 2 seconds.

## Requirements

All requirements can be installed easily through pip:

```
pip3 install numpy opencv-python
```

or on headless systems:

```
pip3 install numpy opencv-python-headless
```

## Usage

```
usage: meteor_corrector [-h] [-s SWATH] [-a ALTITUDE] [-o OUTPUT] INPUT

Correct the warp at the edges of images from Meteor-M2 satellite (and alike)

positional arguments:
  INPUT                 path to the input image

optional arguments:
  -h, --help            show this help message and exit
  -s SWATH, --swath SWATH
                        swath of the satellite (in km)
  -a ALTITUDE, --altitude ALTITUDE
                        altitude of the satellite (in km)
  -o OUTPUT, --output OUTPUT
                        path of the output image
```

### Examples

```
python3 correct.py LRPT_2020_07_09-10_47.png
```

Correct `LRPT_2020_07_09-10_47.png`, output filename will be `LRPT_2020_07_09-10_47-corrected.png`

```
python3 correct.py -o corrected_image.png LRPT_2020_07_09-10_47.png
```

Manually specify the output filename


```
python3 correct.py -a 870 HRPT_N19_20200708_113834.png
```

Correct a NOAA 19 HRPT image (NOAA 19 has altitude of 870km, and the same sized swath)


## License

See `LICENSE`
