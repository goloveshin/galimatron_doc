# galimatron_doc

Documentation for [**Galimatron**](https://github.com/goloveshin/galimatron), a file-based tool that keeps one versioned description of your data in `.gal` files, checks and edits it, and lets your XSLT generate everything else.

The pages are Markdown in `source/`. The diagrams are draw.io files in `drawio/`, exported to `source/images/*.svg`.

## Change the diagrams

Edit a file in `drawio/` with draw.io, then export every diagram again:

```
powershell -File export_drawio.ps1
```

The script needs the draw.io desktop application (`C:\Program Files\draw.io\draw.io.exe`, or pass `-DrawioExe`).

The diagrams of the internals, `drawio/30_dev_*` to `drawio/43_dev_*`, are shown in the "Diagrams of the internals" section of the Reference page. They are **written by scripts** in `tools/drawio_gen/` (Python 3, and the draw.io application for the export):

```
python tools/drawio_gen/pipeline_map.py     # 31_dev_pipeline_map.drawio, the big map
python tools/drawio_gen/small_a.py          # 30, 32 to 35
python tools/drawio_gen/small_b.py          # 36 to 43
python tools/drawio_gen/export_dev.py       # to source/images/*.svg
```

`export_dev.py` removes the fallback PNG that draw.io puts behind every label of an SVG: for the big map they make the file 16 MB instead of 0.6 MB. To change one of these diagrams, change its script and run it again. `svg_tools.py` and `preview_all.py` render an SVG with headless Edge, to look at the result.

## License

[Boost Software License 1.0](LICENSE)
