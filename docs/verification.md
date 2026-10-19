# Verification and limitations

This is a preview release. The checks below describe evidence from the staged source on October 19, 2026; they do not certify every Windows installation, controller firmware or game.

## Automated checks

The staged source passed **75 unittest tests** on Windows using Python 3.12 and the project's installed dependencies:

```powershell
python -m unittest discover -s tests
```

Coverage includes profile validation and storage, preset generation, calibration calculations, source evaluation, normalized output and axis fills, macro scheduling, desktop-output behavior, backend/worker behavior, runtime paths, action captions and startup restoration. Tests use controlled fixtures and mocks where hardware or operating-system output would otherwise be required.

The publication review corrected and added regression coverage for:

- Unsaved edits on exit: Save, Discard and Cancel; failed saving or cancellation keeps the window open. Clean exit does not save a preset.
- Startup restoration: loading the remembered preset bypasses pending-profile autosave, preventing the previous startup name conflict.
- Preset rename: a unique staging file is flushed before publication; a new destination cannot overwrite another preset. The previous managed preset is removed only after successful destination publication. External import files remain intact. Collision and failed-write paths preserve the original.
- Action captions: Save reads current editor values, including programmatic changes. AC8 starters use B **Fire secondary**, X **Cycle weapons** and Y **Change target**. Only exact old default captions are migrated; customized captions and bindings are preserved.
- Backend ownership: each Engine owns private loopback API/USB ports and its own VIIPER process. Closing one mapper does not intentionally stop a server belonging to another instance. A stale startup failure cannot cancel a newer Stop/Start request.
- Dialog lifetime: source/calibration timers stop when the dialog finishes. Deferred deletion preserves immediate result access and removes closed ephemeral dialogs. Reusable editor windows remain available.

These tests establish bounded software behavior, not physical controller operation or successful gameplay. The complete test list is in the repository's `tests` directory.

## Rendered interface check

![Earlier offscreen verification render with original schematic artwork](assets/workspace.png)

The actual Qt interface was rendered and visually inspected at **1640 × 1000** with Segoe UI regular/bold fonts explicitly loaded. The screenshot uses the staged original schematic artwork and an isolated temporary AC8 user preset. The device and output engine were replaced with inert test doubles; the display correctly shows **V1 DISCONNECTED** and output stopped. No controller was polled and no gamepad, keyboard or mouse output was started for this screenshot.

At this size, the game/preset selectors, menus, Xbox symbols, editable action labels, mapping boxes, axis readings, original V1 illustration and input monitor were readable with no observed overlap or clipped controls. This is a static disconnected-state check. It does not establish native Windows title-bar appearance, accessibility, high-DPI behavior, every smaller display size, or live movement visibility.

## Installed-machine integration

The staged Engine launched its private VIIPER server, attached a virtual controller in **2.125 seconds**, streamed neutral reports for **five seconds**, and enumerated Windows XInput slot 0. Cleanup removed the owned server process. No active game controls were injected. This tests the installed USB/IP environment, not first-time installation.

Both the stripped portable and single-file executables rendered successfully with the actual V1 detected and raw axes displayed, then exited with code 0. The first packaging probe exposed a missing offscreen Qt plugin; the specification now retains qoffscreen alongside qwindows and qico. Removed media-codec and copied Microsoft runtime DLLs were absent in the inspected portable directory and single-file archive. Release manifests provide the final file hashes.

## Hardware, game and distribution limits

- **Ace Combat 8 is the only game tested so far. All other game presets are untested.** The owner reports Ace Combat 8 working and supplied the action names above. This is owner feedback, not an independent gameplay qualification. Other game starters are proposed mappings. Verify the selected game/control scheme and every output in the game before relying on a preset.
- Only the original VelocityOne Flightstick V1 is targeted. V2, Flightdeck, HOTAS and other models have not been qualified. Physical input numbering and direction must be confirmed on the actual controller. The schematic is not a factory calibration record.
- No clean Windows-machine installation, first-time driver installation or restart/recovery check was performed. Portable execution on the installed development machine was checked as described above. Installed-development-machine tests cannot prove all release prerequisites are present elsewhere.
- Driver signing, mapper executable signing, antivirus reputation, anti-cheat acceptance, game discovery and elevated-app input restrictions are separate distribution/runtime concerns. A passing suite or screenshot does not establish them. The mapper executable is currently unsigned.
- Macros and the emergency-stop UI depend on Windows scheduling and a responsive application. This software is not a safety controller or a real-time motion controller. Use it for supported game/desktop input, not machinery control.
- Source review and tests do not constitute an exhaustive security audit, independent legal review, manufacturer endorsement or universal compatibility guarantee.

Before a release is described as broadly qualified, exercise the actual release binaries on a clean supported Windows system, install the required driver through its normal flow, verify disconnect/stale-input behavior, and test each claimed game/control scheme with the intended original V1 hardware. Record versions and concrete results rather than treating an app launch as acceptance.



## Public screenshot

The README and project page now use `assets/workspace-live.jpg`, an unedited native screenshot of the running development app with the original V1 connected, the owner's Ace Combat 8 preset loaded and output active. It was captured from the actual window, without mocked inputs. This development build contains photo artwork; the published v0.1.0 download uses schematic artwork. The earlier offscreen verification render above remains separately identified.

## v0.1.1 alternative digital inputs

Added regression coverage for shared L3+R3 and independent inputs, overlapping holds and release, disconnected neutral state, invalid/nested/analog alternatives, list editing and saved-preset round trips. The actual Qt list editor was rendered and visually inspected. Ace Combat 8 remains the only game tested so far.
