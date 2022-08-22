# Wavetable/image converter

Does what it says on the tin - it converts between Serum wavetables and a .png format ideal for manipulation in image editing software.

Each frame of a wavetable is encoded in a column of the image. Partials are represented by pixels with the lowest at the bottom. Brightness corresponds to the magnitude of a partial and hue corresponds to the partial's phase.

## Installation

Make sure you have Python installed - this is tested to work on version 3.10.2, but anything above that should also work.

Run `pip install -r requirements.txt` to install the required libraries.

Then run `python main.py` to bring up the converter GUI.

## Notes

The GUI is mostly self-explanatory, but be careful with the "Include DC offset" option - turning it off will remove the DC offset from the converted image, so keep it turned off when converting back so the program knows to reintroduce it.

Look at `converters.py` if you want (it's quite interesting) but don't open `main.py` unless you want to be confronted with a spaghetti mess of wrangling with Tkinter.