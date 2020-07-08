# Meteor-M2 Geometry Corrector

`meteor_corrector` is a tool for correcting the warp at the edges of images from Meteor-M2 satellite (and alike) written in python3.

It uses OpenCV for image transforms meaning that it can typically process an image in under 2 seconds.

## Requirements

All requirements can be installed easily through pip (it will most likely be `pip3` under Linux):

```
pip install numpy opencv-python
```

## Usage

Simply run with (it will most likely be `python3` under Linux):
```
python correct.py image.png
```

or:

```
./correct.py image.png
```

## License

See `LICENSE`
