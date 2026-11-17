# Models

| File | What | Source | Licence | sha256 |
|---|---|---|---|---|
| `face_detection_yunet_2023mar.onnx` (232589 bytes) | YuNet face detector, used by `scripts/composition_gate.py` (class `Faces`) | opencv_zoo on GitHub, `models/face_detection_yunet/`, downloaded 2026-10-31 with Oxi's OK | MIT, Copyright (c) 2020 Shiqi Yu (`LICENSE-yunet.txt`) | `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4` |

Runtime: `cv2.FaceDetectorYN` needs `opencv-python` 4.8 or newer. the edit machine has
cv2 5.0.0 (Python 3.11.9); both Linux venvs have `opencv-python-headless`
5.0.0.93 (installed 2026-10-31 with Oxi's OK; recorded in the sibling skill,
`../oxi-auto-editor/references/runtime.md`). On Windows the model is loaded from bytes because cv2 cannot
open a path with non-ASCII characters (`<vault>` sits under such paths on
some machines).

Check the file before trusting it:

```
python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" models/face_detection_yunet_2023mar.onnx
```
