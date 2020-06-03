# Meteor-M Geometry Corrector

While intended for Meteor-M satellites it will also work with any other weather satellite in polar orbit.

***

`meteor_corrector` is a tool for removing the warp on the edges of images from Meteor-M satellites (and alike) written in python3.

Since it uses opencv it can be incredibly fast while maintaining readability and quality.

## Requirements

All requirements can be installed easily with pip (depending on your system it may be `pip3`):

```
pip install numpy opencv-python
```

## Running

Depending on your system it may be `python3`.

```
python correct.py image.png
```

or:

```
./correct.py image.png
```

## License

See `LICENSE`