# Blender plugin

# :_: ------------------------------------------------------------------------
#                               Imports
# ----------------------------------------------------------------------------
import os
import bpy
import sys
import site
import logging
import subprocess
import threading

neurovolume_version = "0.1.0a10"
vdb_save_dir = "./output"

# Some copypasta from https://medium.com/@antoine.boucher012/a-method-to-install-python-packages-for-add-ons-plugins-in-blender-windows-blender-4-2-98bcbe10fa81
def display_message(message, title="Notification", icon='INFO'):
    """Show a popup message in Blender."""
    def draw(self, context):
        self.layout.label(text=message)
    def show_popup():
        bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
        return None  # Stops timer
    bpy.app.timers.register(show_popup)
# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_modules_path():
    """Return a writable directory for installing Python packages."""
    return bpy.utils.user_resource("SCRIPTS", path="modules", create=True)

def install_package(package, modules_path):
    """Install a single package using Blender's Python."""
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--target",
            modules_path,
            package
        ])
        logger.info(f"{package} installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}. Error: {e}")
        display_message(f"Failed to install {package}. Check console for details.", icon='ERROR')


install_package(f"neurovolume=={neurovolume_version}", get_modules_path())

import neurovolume as nv
nv.hello()

# :_: ------------------------------------------------------------------------
#                               User Set Path
#                                           Replace these paths with
#                                           the the corresponding paths
#                                           on your machine
# ------------------------------------------------------------------------------\
user_set_output_path = "./output"
user_set_default_nifti = (
    "/Users/joachimpfefferkorn/repos/neurovolume/tests/data/sub-01_task-emotionalfaces_run-1_bold.nii"  # optional
)

# :_: ------------------------------------------------------------------------
#                               Setup
# ------------------------------------------------------------------------------
bl_info = {
    "name": "boldviz",
    "author": "Joachim Pfefferkorn",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 0),
    "location": "",
    "warning": "",
    "category": "Generic",
}
print("boldviz is running")


# :_: ------------------------------------------------------------------------
#                               Backend Functions
# ------------------------------------------------------------------------------


def vdb_frames_sort(entry: dict):
    return int(entry["name"].split(".")[0].split("_")[-1])


def build_volume_data(filepath) -> str:
    path_parts = filepath.split("/")
    filename = nv.get_basename(filepath)
    fps = nv.source_fps(filepath, "NIfTI1")
    if fps == 0:
        return f"{filename}\nStatic Volume"
    else:
        return f"{filename}\nFPS: {fps}"


def load_nifti1(filepath: str, normalize: bool = True):
    vdb_path = os.path.abspath(nv.nifti1_to_VDB(filepath,vdb_save_dir, normalize))
    print("vdb path: ", vdb_path)
    n_frames = nv.num_frames(filepath, "NIfTI1")
    if n_frames == 1:
        bpy.ops.object.volume_import(
            filepath=vdb_path,
            relative_path=False,
            align="WORLD",
            location=(0, 0, 0),
            scale=(1, 1, 1),
        )
        return "static MRI loaded"
    elif n_frames > 1:
        vdb_sequence = []

        for filename in os.listdir(vdb_path):
            if filename.endswith(".vdb"):
                vdb_sequence.append({"name": filename})
            else:
                continue
            vdb_sequence.sort(key=vdb_frames_sort)
        bpy.ops.object.volume_import(
            filepath=filepath,
            directory=vdb_path,
            files=vdb_sequence,
            relative_path=True,
            align="WORLD",
            location=(0, 0, 0),
            scale=(1, 1, 1),
        )
        return "fMRI sequence loaded"


# :_: ------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#                               GUI Functions
# ------------------------------------------------------------------------------


class BoldViz(bpy.types.Panel):
    # Eventually this will probably just be "Load Volumes." Other functionality can go in other panels
    """Main boldviz Panel"""

    bl_label = "boldviz"
    bl_idname = "VIEW3D_PT_nv"
    bl_space_type = "VIEW_3D"  # in the 3D viewport
    bl_region_type = "UI"  # in the UI panel
    bl_category = "boldvz"  # name of panel

    def draw(self, context):
        self.layout.prop(context.scene, "path_input")
        self.layout.operator("load.volume", text="Load VDB from NIfTI")

        if hasattr(context.scene, "volume_info_text"):
            self.layout.label(text="🧠 Last Loaded Volume:")
            text = context.scene.volume_info_text
            for line in text.split("\n"):
                self.layout.label(text=f"     {line}")
        else:
            self.layout.label(text="no info")


class LoadVolume(bpy.types.Operator):  # LLM: drop-in rewrite for reactive loading
    bl_idname = "load.volume"
    bl_label = "Load Volume"

    _timer = None
    _path = None
    _step = 0

    def execute(self, context):
        self._path = context.scene.path_input
        if not os.path.exists(self._path):
            context.scene.volume_info_text = f"⚠️ file '{self._path}' does not exist"
            self.report({"INFO"}, "file does not exist")
            return {"FINISHED"}
        context.scene.volume_info_text = "⏳ Loading..."
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        # BUG: volume info does not display until you click away!
        if event.type == "TIMER":
            if self._step == 0:
                context.scene.volume_info_text = "⏳ Parsing header..."
            elif self._step == 1:
                load_nifti1(self._path)
                context.scene.volume_info_text = "📊 Building VDB data..."
            elif self._step == 2:
                data = build_volume_data(self._path)
                context.scene.volume_info_text = data
                self.report({"INFO"}, "Volume loaded")
                wm = context.window_manager
                wm.event_timer_remove(self._timer)
                return {"FINISHED"}
            self._step += 1
        return {"RUNNING_MODAL"}


# :_: ------------------------------------------------------------------------
#                               Property Registration
# ------------------------------------------------------------------------------


def register_properties():
    bpy.types.Scene.path_input = bpy.props.StringProperty(
        name="NIfTI File",
        description="Enter path to folder containing .npy files",
        default=user_set_default_nifti,
    )
    bpy.types.Scene.volume_info_text = bpy.props.StringProperty(
        name="Volume Info", description="", default="   not loaded yet"
    )


def unregister_properties():
    del bpy.types.Scene.path_input
    del bpy.types.Scene.volume_info_text
    # del bpy.types.Scene.volume_status


classes = [BoldViz, LoadVolume]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    unregister_properties()


if __name__ == "__main__":
    register()


print("eof __init__.py of boldviz")
