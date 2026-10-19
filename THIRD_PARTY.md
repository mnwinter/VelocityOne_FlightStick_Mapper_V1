# Third-party components and artwork

This is an independent community application with no manufacturer affiliation or endorsement. Turtle Beach and VelocityOne are their owners' trademarks. Public controller artwork is an original schematic illustration. Release binaries use that original illustration. The README/project-page screenshot is a native capture of the earlier development app and shows its photo-based controller view; it is not the artwork shipped in v0.1.0. Third-party imagery is not relicensed under the mapper GPL.

The mapper is GPL-3.0 under the root LICENSE. Dependencies retain their respective terms. See [dependency source and replacement instructions](docs/dependency-sources.md). `licenses/dependency-inventory.json` records notice provenance and hashes; the final release binary manifest is separate. Notice collection is not a distribution certification.

Python 3.12.14's actual runtime license is `licenses/Python-3.12.14-LICENSE.txt`. pygame-ce 2.5.8 and SDL notices are under `licenses/pygame-ce-2.5.8/`; SDL reports 2.32.10. The public build selects joystick/event/display functionality and omits unused audio/font/image-codec DLLs and the bundled pygame font. Qt/PySide6/shiboken6 6.12.0 source-level licenses and third-party attribution metadata are under `licenses/qt-6.12.0/`, with LGPL-3.0 and GPL texts also included. The public spec retains Qt Core/Gui/Widgets/Network and qwindows/qoffscreen/qico plugins; other Qt modules and plugins are filtered out. Notice folders remain a conservative source-level superset, not a list of shipped modules. No commercial Qt license is claimed. Commercial-only metadata stubs were preserved locally outside the public project and removed from the public notice selection.

Public binary builds omit copied Microsoft VC runtime, UCRT and API-set DLLs. Windows 11 and the official Microsoft Visual C++ x64 runtime are prerequisites. Their terms are separate from this project's GPL license. See the dependency guide for official download/support links and qualification limits.

## Historical upstream evidence

- **VIIPER v0.9.0**, released October 10, 2026 UTC. Upstream: https://github.com/Alia5/VIIPER/releases/tag/v0.9.0 . The standalone executable's Authenticode signature was verified valid, signer Peter Repukat. GPL-3.0; license in `licenses/VIIPER-GPL-3.0.txt`; corresponding release source in `backend/VIIPER-v0.9.0-source.zip`. Our app communicates using the documented TCP protocol rather than linking libVIIPER. Maintenance evidence: inspected main commit `20aa112c6ea47187526dd88d0fd666a68a5f4416`, October 15, 2026. This is current evidence, not a guarantee of future maintenance.
- **usbip-win2 v0.9.8.1**, released September 27, 2026 UTC. https://github.com/vadimgrn/usbip-win2/releases/tag/v.0.9.8.1 . The downloaded x64 installer has a valid Authenticode signature. The upstream project documents signed Windows drivers. Installer signature verification does not establish successful driver installation or compatibility on this PC. BSD-2-Clause; see `licenses/USBIP-BSD-2-Clause.txt`.
- **PySide6 / Qt 6.12**, Qt Widgets bindings. https://doc.qt.io/qtforpython-6/licenses.html . Applicable open-source license texts and component notices are included. Source and portable builds provide modification routes; see the dependency guide for remaining qualification.
- **pygame-ce 2.5.8 / SDL2**, joystick input. https://pyga.me/docs/ref/joystick.html . pygame-ce LGPL-2.1; SDL zlib license. Package license texts included in `licenses`.
- **Python 3.12** and **PyInstaller 6.22.3** supply the packaged runtime/bootloader, under their upstream license terms.
- Manufacturer photographs from the official original-V1 product gallery were used only during earlier local development. They are excluded from rebuilt release binaries. The actual development-app screenshot in the README/project page shows that older photo-based view.

No x360ce or ViGEm binary, client library, driver, or running process is required by this application. Existing installations are preserved.

Release controller illustrations replace the earlier manufacturer photographs.
