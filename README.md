# Wavetable/image converter

Does what it says on the tin - it converts between Serum wavetables and a .png format ideal for manipulation in image editing software.

Each frame of a wavetable is encoded in a column of the image. Partials are represented by pixels with the lowest at the bottom. Brightness corresponds to the magnitude of a partial and hue corresponds to the partial's phase.

I hope the GUI is somewhat self-explanatory. This is the first README I've ever actually had to write, so it is awful and does not conform to any actual standards.

## Installation

Make sure you have Python installed - this is tested to work on 3.10.

Run `pip install -r requirements.txt` to install the required libraries.

Then running `python main.py` should bring up the converter GUI.