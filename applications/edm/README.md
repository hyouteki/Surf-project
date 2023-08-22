# EDM application
## EDM layout
| E  | F  | F# | G  |
| -- | -- | -- | -- |
| C  | C# | D  | D# |
| G# | A  | A# | B  |
| E  | F  | F# | G  |
| C  | C# | D  | D# |

> Maps the physical input to digital<br>
> **P.S.** : This is a CLI application

## Quick start
- Install some required python libraries
  <br><br>
  ``` console
  pip install termcolor
  pip install pyaudio
  ```
- Launch the EDM via
  <br><br>
  ``` console
  python edm.py
  ```
  > **IMPORTANT**: This will not work if Arduino code is not running in parallel.

## Courtesy
- [Pitch playing logic](https://stackoverflow.com/a/53231212)