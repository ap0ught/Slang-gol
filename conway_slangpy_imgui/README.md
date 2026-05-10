# Conway SlangPy ImGui Demo

Small proof-of-concept desktop app for Conway's Game of Life:

- ImGui Bundle control panel
- Slang/SlangPy update integration point
- CPU fallback when SlangPy is unavailable

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\\Scripts\\activate   # Windows PowerShell
pip install -r requirements.txt
```

Or use the install helper:

```bash
# from the repository root
cd conway_slangpy_imgui && ./install.sh
```

## Run

```bash
python app.py
```

## Current architecture

`current_grid -> Slang update -> next_grid -> swap buffers`

`app.py` currently keeps a CPU fallback path active so the demo still runs while the
exact SlangPy tensor/buffer binding is adapted for your installed SlangPy version.

## Future task: texture rendering in ImGui

The current app includes the simulation + control panel. The next feature is
uploading `life.to_rgba_image()` to an ImGui texture and rendering it, e.g.:

```python
image = life.to_rgba_image()
texture_id = upload_image_to_imgui_texture(image)
imgui.image(texture_id, (512, 512))
```

The exact upload helper depends on the selected `imgui_bundle` renderer backend.
