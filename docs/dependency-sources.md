# Dependency sources and distribution qualification

Reviewed October 19, 2026. This is technical evidence, not legal certification. `licenses/dependency-inventory.json` records notice provenance and hashes. Notice collection is a conservative source-level superset; the actual public binary manifest must be checked after rebuilding. It must not be inferred from the notice folders.

## Versions and corresponding sources

| Dependency | Version | Official source |
| --- | --- | --- |
| CPython | 3.12.14, actual build interpreter | https://github.com/python/cpython/tree/v3.12.14 |
| PySide6 / shiboken6 | 6.12.0 | https://github.com/pyside/pyside-setup/tree/v6.12.0 |
| Qt | 6.12.0 | https://download.qt.io/archive/qt/6.12/6.12.0/submodules/ ; https://github.com/qt/qtbase/tree/v6.12.0 |
| pygame-ce | 2.5.8 | https://pypi.org/project/pygame-ce/2.5.8/#files |
| SDL | 2.32.10 reported by pygame | https://github.com/libsdl-org/SDL/tree/release-2.32.10 |
| PyInstaller | 6.22.3 | https://github.com/pyinstaller/pyinstaller/tree/v6.22.3 |
| VIIPER | 0.9.0 | https://github.com/Alia5/VIIPER/tree/v0.9.0 |
| usbip-win2 | 0.9.8.1 | https://github.com/vadimgrn/usbip-win2/tree/v.0.9.8.1 |

Python's license was copied from the actual runtime. Qt/PySide licenses and component attribution metadata were collected from official 6.12.0 source tags. pygame notices came from the exact source distribution: https://files.pythonhosted.org/packages/26/2d/0f942ec31d558a6a1f2fd0df9965ff0055f165ed5b8d36f6509b1f3768a2/pygame_ce-2.5.8.tar.gz . Supplemental SDL_ttf, OpenSSL, libffi, xz, WavPack and libxmp notices came from official repositories, sometimes moving branches; the inventory records retrieved hashes. These supplementary notices do not imply the components are all distributed. The public spec excludes pygame audio/font/image-codec DLLs and the bundled font, so their source correspondence is not required for this package if final artifact inspection confirms their absence.

For binary distribution, retain and host the exact dependency source archives/build inputs where required. A moving source URL or an embedded application `.py` file alone does not establish complete corresponding-source compliance. The GPL license for the mapper does not override third-party terms.

The release dependency-source asset is `VelocityOneMapper-Dependency-Sources.zip`. It retains tagged source snapshots for CPython, Qtbase, PySide6/shiboken6, pygame-ce, SDL, PyInstaller, usbip-win2 and VIIPER, with a manifest of download URLs and SHA-256 hashes. Application source/build inputs are provided separately by this GPL repository and release. Retained source archives include upstream build instructions; successful reproduction of signed upstream binaries is not claimed. GitHub snapshots may omit external submodule/dependency contents fetched by upstream build scripts, so those inputs must also be resolved and preserved when required. Do not describe this collection alone as a fully reproduced dependency toolchain.

## Backend pins

Local executable hashes matched GitHub release-asset SHA-256 digests on review:

| Local file | Official URL | SHA-256 |
| --- | --- | --- |
| `viiper.exe` | https://github.com/Alia5/VIIPER/releases/download/v0.9.0/viiper-windows-amd64.exe | `142c144f6abee8b8a5f6a1abbc7018683444de71d2e45102cde6aaab9b2223e6` |
| `USBip-0.9.8.1-x64.exe` | https://github.com/vadimgrn/usbip-win2/releases/download/v.0.9.8.1/USBip-0.9.8.1-x64.exe | `38cad6d4432b52d5bb9409d9ad03b72fdffc4ada4cd3a48fbeca1a2752a8518a` |

Local `VIIPER-v0.9.0-source.zip`: SHA-256 `303c9ca3613863dc8eb9fa432f092d70b3240c514d898920199afa68b5651918`; contents include the `VIIPER-0.9.0` tree and build/workflow files. Reproduction of the signed upstream executable has not been established. Retain the reviewed source archive alongside each binary release. Investigate archive hash changes rather than silently changing pins.

## Replacing LGPL libraries and rebuilding

See [Qt licensing guidance](https://doc.qt.io/qtforpython-6/licenses.html) and included LGPL texts. The application is GPL-3.0; library modification and reverse engineering for debugging those modifications are permitted under applicable terms. No commercial Qt entitlement is assumed.

For source execution, create a Python 3.12 virtual environment, install the pinned requirements, and run `app.py`. Install an interface-compatible modified PySide6/shiboken6/Qt or pygame-ce build into that environment in place of its original wheel, then run or rebuild the application using `build.ps1`. Preserve all required dependency source/build inputs and notices. Use the public artwork and reviewed backend downloads.

The portable directory build exposes shared libraries for replacement. With the app closed, replace the library and matching bindings/plugins as a coherent interface-compatible set, preserving directory layout. Do not mix arbitrary Qt versions, architectures or Debug/Release binaries. Then launch and verify behavior. Single-file builds recreate embedded libraries on startup; editing a temporary extraction directory is not a persistent replacement mechanism. Single-file publication therefore also needs a complete corresponding-source/rebuild route. The portable build is the recommended practical modification route.

The public spec permits only Qt Core, Gui, Widgets and Network DLLs, plus qwindows/qoffscreen/qico plugins. It excludes unused PDF, Virtual Keyboard, QML, Quick and other plugin dependency closures. PE inspection shows the retained qwindows/qoffscreen/qico plugins require only Core/Gui. Different Qt modules have different licensing options; never label every Qt module LGPL.

pygame's required joystick/display/event modules and SDL2.dll were inspected: they require no external media codecs. Public packaging excludes mixer, mixer_music, font, freetype, imageext and MIDI modules, and filters SDL2_image, SDL2_mixer, SDL2_ttf, FreeType, JPEG, Ogg/Opus, PNG, TIFF, WavPack, WebP, libxmp and PortMidi DLLs from all destinations. The normal pygame image/surface helpers can remain because their inspected PE imports require SDL2 rather than those codecs. Final archive inspection and real SDL polling must confirm the stripped package works.

## Microsoft runtime prerequisites

Public builds omit copied `VCRUNTIME*`, `MSVCP*`, `CONCRT*`, `ucrtbase.dll` and `api-ms-win*` DLLs. Windows 11 supplies system UCRT/API-set components. Users must install the official supported **Microsoft Visual C++ x64 runtime** if it is absent. The app is therefore packaged with its Python/Qt/pygame dependencies but still has Windows runtime prerequisites.

- [Official supported runtime downloads and requirements](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist)
- [Official x64 installer](https://aka.ms/vc14/vc_redist.x64.exe)
- [Microsoft redistribution terms guidance](https://learn.microsoft.com/cpp/windows/redistributing-visual-cpp-files)

Microsoft's guidance ties redistribution to applicable Visual Studio terms. Presence inside a wheel is not proof of the publisher's entitlement. Omitting copied Microsoft DLLs removes that direct redistribution from this app's package; it does not certify every embedded upstream installer's internal components. Final archive inspection and clean-machine prerequisite testing remain necessary. Driver installation and in-game compatibility are separate acceptance gates.

## Remaining qualification

The collected notices are necessary evidence, not a complete legal audit. Check the final release binary manifest against the selected DLLs, source availability/rebuild completeness, and embedded installer terms. Codec-version qualification applies only if removed codecs are reintroduced. Hashes and signatures provide provenance evidence; they do not establish clean-machine installation, compatibility, security, or physical input correctness.

