import numpy as np
import soundfile as sf
from PIL import Image
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
import os.path
from time import perf_counter
import converters as conv

def wavetable2image(input: str, output: str, **kwargs):
    audio, rate = sf.read(input)
    if audio.ndim != 1:
        raise ValueError("Invalid wavetable: not mono")
    hsv_array = conv.wave2hsv(audio, **kwargs)
    img = Image.fromarray(hsv_array, mode="HSV")
    img = img.convert("RGB")
    img = img.transpose(2) # rotate 90 degrees anticlockwise
    img.save(output)

def image2wavetable(input: str, output: str, **kwargs):
    img = Image.open(input)
    img = img.transpose(4) # rotate 90 degrees clockwise
    img = img.convert("HSV")
    hsv_array = np.asarray(img)
    audio = conv.hsv2wave(hsv_array, **kwargs).astype(np.float32)
    sf.write(output, audio, samplerate=44100)

class ConverterFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.columnconfigure(0, weight=1)

        self.label_width = 30
        self.filetypes = (
            (".wav files", "*.wav"),
            (".png files", "*.png")
        )

        self.input_filenames = tuple()
        self.output_dir = ""

        self.init_tk_vars()

        self.lf_input = self.make_input_frame()
        self.lf_output = self.make_output_frame()
        self.lf_options = self.make_options_frame()
        self.btn_convert = ttk.Button(self, text="Convert!", command=self.convert)
        self.lbl_status = ttk.Label(self, textvariable=self.var_status)

        self.lf_input.grid(column=0, row=0)
        self.lf_output.grid(column=0, row=1)
        self.lf_options.grid(column=0, row=2)
        self.btn_convert.grid(column=0, row=3)
        self.lbl_status.grid(column=0, row=4)

        self.expand(self)

        self.update_path_vars()

    def expand(self, frame: ttk.Frame):
        for child in frame.winfo_children(): 
            child.grid_configure(sticky="ew", padx=3, pady=3)

    def init_tk_vars(self):
        self.var_input_path = tk.StringVar()
        self.var_output_path = tk.StringVar()
        self.var_frame_size = tk.IntVar(value=2048)
        self.var_limit_partials = tk.BooleanVar(value=False)
        self.var_partial_cutoff = tk.IntVar(value=256)
        self.var_include_dc_offset = tk.BooleanVar(value=True)
        self.var_allow_incomplete = tk.BooleanVar(value=True)
        self.var_status = tk.StringVar(value="made by mos")

    def make_input_frame(self):
        lf_input = ttk.Labelframe(self, text="Input")
        lbl_input_path = ttk.Label(lf_input, textvariable=self.var_input_path, width=self.label_width)
        btn_input_browse = ttk.Button(lf_input, text="Browse...", command=self.input_dialog)
        lbl_input_path.grid(column=0, row=0)
        btn_input_browse.grid(column=0, row=1)
        self.expand(lf_input)
        return lf_input

    def make_output_frame(self):
        lf_output = ttk.Labelframe(self, text="Output")
        lbl_output_path = ttk.Label(lf_output, textvariable=self.var_output_path, width=self.label_width)
        btn_output_browse = ttk.Button(lf_output, text="Browse...", command=self.output_dialog)
        lbl_output_path.grid(column=0, row=0)
        btn_output_browse.grid(column=0, row=1)
        self.expand(lf_output)
        return lf_output

    def make_options_frame(self):
        def toggle_cutoff_box():
            if self.var_limit_partials.get():
                box_partial_cutoff["state"] = "normal"
            else:
                box_partial_cutoff["state"] = "disabled"

        lf_options = ttk.Labelframe(self, text="Options")

        lbl_frame_size = ttk.Label(lf_options, text="Frame size:")
        box_frame_size = ttk.Combobox(lf_options, textvariable=self.var_frame_size)
        tick_limit_partials = ttk.Checkbutton(lf_options, text="Limit partials?", variable=self.var_limit_partials, command=toggle_cutoff_box)
        lbl_partial_cutoff = ttk.Label(lf_options, text="Partial cutoff:")
        box_partial_cutoff = ttk.Combobox(lf_options, textvariable=self.var_partial_cutoff)
        tick_include_dc_offset = ttk.Checkbutton(lf_options, text="Include DC offset?", variable=self.var_include_dc_offset)
        tick_allow_incomplete = ttk.Checkbutton(lf_options, text="Allow incomplete frames?", variable=self.var_allow_incomplete)
        
        box_frame_size["values"] = (1024, 2048, 4096)
        box_partial_cutoff["values"] = (256, 512, 1024)
        toggle_cutoff_box()

        lbl_frame_size.grid(column=0, row=0)
        box_frame_size.grid(column=0, row=1)
        tick_limit_partials.grid(column=0, row=2)
        lbl_partial_cutoff.grid(column=0, row=3)
        box_partial_cutoff.grid(column=0, row=4)
        tick_allow_incomplete.grid(column=0, row=5)

        self.expand(lf_options)

        return lf_options

    def input_dialog(self):
        self.input_filenames = fd.askopenfilenames(
            parent=self,
            title="Open wavetable(s) or image(s)...",
            filetypes=self.filetypes,
        )
        self.update_path_vars()

    def output_dialog(self):
        self.output_dir = fd.askdirectory(
            parent=self,
            title="Select output directory..."
        )
        self.update_path_vars()

    def update_path_vars(self):
        if len(self.input_filenames) == 1:
            self.var_input_path.set(self.input_filenames[0])
        else:
            self.var_input_path.set(f"{len(self.input_filenames)} input files selected")

        if self.output_dir == "":
            self.var_output_path.set("No output directory selected")
        else:
            self.var_output_path.set(self.output_dir)

    def convert(self):
        self.var_status.set("Conversion started...")
        start_time = perf_counter()
        converted_counter = 0

        # forgor to set output directory?
        if self.output_dir == "":
            self.var_status.set("Please select an output directory...")
            return

        for path in self.input_filenames:
            filename = os.path.basename(path)
            name = filename[:-4]
            extension = filename[-4:]
            try:
                if extension == ".wav":
                    wavetable2image(
                        path,
                        f"{self.output_dir}/{name}.png",
                        frame_size=self.var_frame_size.get(),
                        include_dc_offset=self.var_include_dc_offset.get(),
                        limit_partials=self.var_limit_partials.get(),
                        partial_cutoff=self.var_partial_cutoff.get(),
                        allow_incomplete=self.var_allow_incomplete.get()
                    )
                    converted_counter += 1
                elif extension == ".png":
                    image2wavetable(
                        path,
                        f"{self.output_dir}/{name}.wav",
                        frame_size=self.var_frame_size.get(),
                        include_dc_offset=self.var_include_dc_offset.get()
                    )
                    converted_counter += 1
            except ValueError as e:
                self.var_status.set(e)
                return

        elapsed = perf_counter() - start_time
        self.var_status.set(f"Converted {converted_counter} file(s) in {elapsed:.3f} s.")


def main():
    window = tk.Tk()
    window.title("wt/image converter")
    window.resizable(False, False)
    window.columnconfigure(0, weight=1)
    frame = ConverterFrame(window)
    frame.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)
    window.mainloop()

if __name__ == "__main__":
    main()