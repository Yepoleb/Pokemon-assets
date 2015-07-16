echo "Creating directories"
python3 makedirs.py
echo "Exporting tilesets"
python3 export_tilesets.py
echo "Exporting maps"
python3 export_maps.py
echo "Exporting sprites"
python3 sprites.py
echo "Exporting font"
python3 textfont.py
echo "Exporting textbox textures"
python3 textboxes.py
echo "Exporting bag textures"
python3 bag.py
echo "Copying static files"
./copystatic.sh

