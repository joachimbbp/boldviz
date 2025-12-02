# 🌈 BoldViz 
A [Blender](https://www.blender.org/) plugin for visualizing neurological MRI and fMRI scans. It uses the [neurovolume](https://github.com/joachimbbp/neurovolume) library, which is currently in pre-release and does not support all `.nii` formats.

⚠️ This project is currently under development.

# 🏗️ Instructions
Run `download_test_data.py` to download the test dataset (optional). This is the default `NIfTI` file that appears in the Blender plugin. An fMRI dataset can be found in the "Dataset Citation" section below, if you wish to test that.

Install the Blender plugin using one of the following methods:
- With [Jacques Lucke's vsCode extension for Blender](https://github.com/JacquesLucke/blender_vscode) (recommended)
- [Via the Add-ons section](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html)
- Copy-pasting the add-on into Blender's [Text-editor](https://docs.blender.org/manual/en/latest/editors/text_editor.html) and then clicking the triangular "play" button to run.

# 🧠 Dataset Citation
This software was tested using the following datasets.

Isaac David and Victor Olalde-Mathieu and Ana Y. Martínez and Lluviana Rodríguez-Vidal and Fernando A. Barrios (2021). Emotion Category and Face Perception Task Optimized for Multivariate Pattern Analysis. OpenNeuro. [Dataset] doi: 10.18112/openneuro.ds003548.v1.0.1

[OpenNeuro Study Link](https://openneuro.org/datasets/ds003548/versions/1.0.1)

[Direct Download Link for T1 Anat test file](https://s3.amazonaws.com/openneuro.org/ds003548/sub-01/anat/sub-01_T1w.nii.gz?versionId=5ZTXVLawdWoVNWe5XVuV6DfF2BnmxzQz)

[Direct Download Link for BOLD test file](https://s3.amazonaws.com/openneuro.org/ds003548/sub-01/func/sub-01_task-emotionalfaces_run-1_bold.nii.gz?versionId=tq8Y3ktm31Aa8JB0991n9K0XNmHyRS1Q)