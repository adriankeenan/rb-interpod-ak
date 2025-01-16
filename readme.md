# Interpod

My personal fork of the Interpod rockbox theme for 320x240 resolution devices

```
┌─────────────────────────────────────────────────────────────────────────┐
│   d888888b d8b   db d888888b d88888b d8888b. d8888b.  .d88b.  d8888b.   │
│     `88'   888o  88 `~~88~~' 88'     88  `8D 88  `8D .8P  Y8. 88  `8D   │
│      88    88V8o 88    88    88ooooo 88oobY' 88oodD' 88    88 88   88   │
│      88    88 V8o88    88    88~~~~~ 88`8b   88~~~   88    88 88   88   │
│     .88.   88  V888    88    88.     88 `88. 88      `8b  d8' 88  .8D   │
│   Y888888P VP   V8P    YP    Y88888P 88   YD 88       `Y88P'  Y8888D'   │
│                                                                         │
│                                                                         │
│                              Rockbox Theme                              │
│   Rev. 17                                         by Christian Soffke   │
│   2023-06-10                                                 CC-BY-SA   │
│                                                                         │
│   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│   ┃                                                                  ┃  │
│   ┃       Originally loosely based on David Barkan's AMusicPod       ┃  │
│   ┃                                                                  ┃  │
│   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│                                                                         │
│    Changelog:                                                           │
│                                                                         │
│    Rev. 17 (2013-06-10):                                                │
│      - Switch to 16bit BMP to prevent redundant dithering of backdrop   │
│                                                                         │
│    Rev. 16 (2013-06-10):                                                │
│      - Use %x instead of %xd for backdrop                               │
│                                                                         │
│    Rev. 15 (2023-06-10):                                                │
│      - Pre-dithered backdrop for improved compatibility with older      │
│        builds of Rockbox                                                │
│                                                                         │
│    Rev. 14 (2023-06-10):                                                │
│      - Album art has rounded corners                                    │
│      - New backdrop                                                     │
│      - New progress bar.                                                │
│      - Increase height of progress bar when ffw-ing or rewinding        │
│      - New volume bar. Show warning when volume above 0dB               │
│      - Use "Rockbox" in list titles where "iPod" was used before        │
│      - Set black as foreground color to improve usability of keyboard   │
│      - Pink accent color now stays fixed (f24e61). Other theme variants │
│        have been removed. You can still search&replace in WPS file      │
│        to pick another value.                                           │
│      - Fix visual glitch in bottom bar                                  │
│                                                                         │
│    Rev. 13 (2022-12-26):                                                │
│      - Don't display battery percentage on QuickScreen if it is         │
│        already displayed in the menu bar                                │
│                                                                         │
│    Rev. 12 (2022-12-26):                                                │
│      - Optionally display battery percentage in all menus               │
│      - Added minimalistic icons necessary to support basic RB           │
│        functionality                                                    │
│                                                                         │
│    Rev. 11 (2021-10-13):                                                │
│      - WPS Design Overhaul                                              │
│                                                                         │
│    Rev. 10 (2021-10-04):                                                │
│      - Added theme with black accent color                              │
│                                                                         │
│    Rev. 9 (2021-08-25):                                                 │
│      - Added sleep timer                                                │
│      - Added volume bar to QuickScreen                                  │
│        (requires recent dev version of Rockbox)                         │
│                                                                         │
│    Rev. 8 (2021-08-23):                                                 │
│      - Added Repeat One/Shuffle/AB badges                               │
│      - Added Lossless indicator                                         │
│                                                                         │
│    Rev. 7 (2021-04-02):                                                 │
│      - Adjust the accent color (i.e. the color of the volume bar,       │
│        artist/album + selected line) by changing the Foreground         │
│        and Line Selector setting in Settings->Theme Settings->Colors.   │
│        Defaults to pink. A pre-built gray theme can be accessed by      │
│        renaming the file name extension of "Interpod (Gray).txt" in the │
│        themes subfolder to ".cfg" and then selecting it in Rockbox.     │
│                                                                         │
│    Rev. 6 (2021-03-31):                                                 │
│      - New player state and battery icons                               │
│      - Subtle changes to titlebar                                       │
│                                                                         │
│    Rev. 5 (2021-03-28):                                                 │
│      - Larger font sizes in title bar and on WPS for improved legibility│
│      - Filetype colors are now reset when theme is loaded               │
│      - Removed hack that was used to prevent visual glitch, since       │
│        it should not be needed anymore in latest (development) version  │
│        of Rockbox                                                       │
│                                                                         │
│    Rev. 4 (2021-02-26):                                                 │
│      - New Shuffle and Repeat icons                                     │
│                                                                         │
│    Rev. 3 (2021-02-23):                                                 │
│      - Fix album title not scrolling                                    │
│      - Display battery percentage on WPS                                │
│      - change status bar font                                           │
│                                                                         │
│    Rev. 2 (2021-02-23):                                                 │
│      - Scroll track title on bottom of SBS                              │
│      - Shift track title to the left when album art is unavailable      │
│      - Fix cut off remaining time on WPS                                │
│      - Use negative alignment to prepare for different screen sizes     │
│      - Scroll elapsed and remaining time as necessary                   │
│                                                                         │
│    Rev. 1 (2021-02-22):                                                 │
│      - Don't display file name twice if artist and title are both       │
│        missing                                                          │
│      - Fix visual glitch in title bar when stopping playback from WPS   │
│        and returning to file or database browser                        │
│                                                                         │
│    Rev. 0 (2021-02-22):                                                 │
│      - Initial Release                                                  │
│                                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```