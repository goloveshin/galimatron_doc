# galimatron_doc

Documentation for [**Galimatron**](https://github.com/goloveshin/galimatron), a file-based tool that keeps one versioned description of your data in `.gal` files, checks and edits it, and lets your XSLT generate everything else.

The pages are Markdown in `source/`. The diagrams are draw.io files in `drawio/`, exported to `source/images/*.svg`.

## Change the diagrams

Edit a file in `drawio/` with draw.io, then export every diagram again:

```
powershell -File export_drawio.ps1
```

The script needs the draw.io desktop application (`C:\Program Files\draw.io\draw.io.exe`, or pass `-DrawioExe`).

## License

[Boost Software License 1.0](LICENSE)
