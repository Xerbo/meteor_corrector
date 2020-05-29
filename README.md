# Meteor-M Geometry Corrector

While intended for Meteor-M satellites it will also work with any other weather satellite in polar orbit.

***

`meteor_corrector` is a python tool for removing the warp on the edges of images from Meteor-M satellites.

Since it uses opencv it can be incredibly fast while not sacrificing quality (LANCZOS4 interpolation + sharpening does not take more than 3 seconds on decent hardware)

## Requirements

All requirements can be installed easily with pip:

```  
pip3 install numpy scipy opencv-python
```

## Running

```
python3 correct.py image.png
```

or:

```
./correct.py image.png
```

## License

See `LICENSE`