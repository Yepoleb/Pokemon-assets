#Pokemon-assets

Scripts for exporting Pokémon assets.

##Dependencies

* [Pillow]
* [TileCodecs]
* My [fork of pytmxlib] with csv/xml export
* My [fork of Blue Spider] with map connections parsing

##Usage

Copy a Pokemon Fire Red rom to ./firered.gba
Run `./export.sh`
If you don't want to run the full script, make sure to execute `makedirs.py` 
before anything else and `export_tilesets.py` before `export_maps.py`.



[Pillow]:http://python-pillow.github.io/
[TileCodecs]:https://github.com/Yepoleb/TileCodecs
[fork of pytmxlib]:https://github.com/Yepoleb/pytmxlib
[fork of Blue Spider]:https://github.com/Yepoleb/blue-spider
