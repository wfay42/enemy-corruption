magick convert -crop 489x489+675+8 shiori-stand.png shiori-cropped.png
magick convert -resize 144x144 shiori-cropped.png shiori-cropped-resized.png

magick convert -crop 640x640+683+4 arisa-stand.png arisa-cropped.png
magick convert -resize 144x144 arisa-cropped.png arisa-cropped-resized.png

magick convert -crop 689x689+604+4 arisa-pet-stand.png arisa-pet-cropped.png
magick convert -resize 144x144 arisa-pet-cropped.png arisa-pet-cropped-resized.png

magick convert +append shiori-cropped-resized.png arisa-cropped-resized.png arisa-pet-cropped-resized.png petroids.png

 
