#Pokemon-assets

Scripts for exporting Pokémon assets.

##Dependencies

* [Pillow]
* [TileCodecs]
* My [fork of pytmxlib] with csv/xml export
* My [fork of Blue Spider] with map connections parsing

##Usage

1. Copy a Pokemon Fire Red rom to ./firered.gba (md5: e26ee0d44e809351c8ce2d73c7400cdd)
2. Run `./export.sh`  

If you don't want to run the full script, make sure to execute `makedirs.py` before anything else and `export_tilesets.py` before `export_maps.py`.



[Pillow]:http://python-pillow.github.io/
[TileCodecs]:https://github.com/Yepoleb/TileCodecs
[fork of pytmxlib]:https://github.com/Yepoleb/pytmxlib
[fork of Blue Spider]:https://github.com/Yepoleb/blue-spider

