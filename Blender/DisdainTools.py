# DisdainTools
# Written by Nash Muhandes for DISDAIN
# https://store.steampowered.com/app/2113270/DISDAIN/
# https://github.com/MischiefDonut/DisdainDevKit
# Script license: MIT

import os
import bpy
import math
import sys
import time
import mathutils as mu

from bpy.props import *

bl_info = \
{
    "name" : "DisdainTools",
    "author" : "Nash Muhandes",
    "version" : (1, 0, 0),
    "blender" : (2, 7, 9),
    "location" : "Render",
    "description" : "",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "Render",
}

# SCRIPT CONFIGURATION (TODO: expose these as checkboxes on the UI

# Set use_anim_clips to True to use per-animation-clip workflow
# False if using old-style workflow where all of the animations is a single giant and long timeline
use_anim_clips = True

# Set use_decoupled_anim to True to generate decoupled-animation-style scripts
# (MODELEF will NOT be generated if True)
# Setting this to True will also force every State in ZScript to be '0000 A'.
use_decoupled_anim = True

# Set collapse_similar_states to merge similar states into a single line
collapse_similar_states = True

# Set animspec_comment_embed_fps to True, to embed the FPS values in the generated animspec_comment
animspec_comment_embed_fps = True

# Set generate_a_movepos to True to generate movement in XYZ
generate_a_movepos = True

# END SCRIPT CONFIGURATION

class DisdainToolsSettings(bpy.types.PropertyGroup):
    targ = StringProperty\
    (
        name = "Target object",
        description = """The Empty object to use for A_Run calculation""",
        default = ""
    )

    filepath_arunspeeds = StringProperty\
    (
        name = "A_Run speeds output path",
        description = """Where to save the generated script""",
        default = "",
        subtype = 'FILE_PATH'
    )

    filepath_scripts = StringProperty\
    (
        name = "Animation script output path",
        description = """Where to save the generated script""",
        default = "",
        subtype = 'FILE_PATH'
    )


class DisdainToolsGenARunSpeedsOperator(bpy.types.Operator):
    bl_idname = "render.disdaintools_genarunspeeds_operator"
    bl_label = "DisdainToolsGenARunSpeeds Operator"
    bl_options = { 'REGISTER' }

    def execute(self, context):
        self.generate_a_run_speeds(context.scene, context.scene.disdaintools.targ, context.scene.disdaintools.filepath_arunspeeds, context.scene.frame_start, context.scene.frame_end)
        self.generate_a_movepos_speeds(context.scene, context.scene.disdaintools.targ, context.scene.disdaintools.filepath_arunspeeds, context.scene.frame_start, context.scene.frame_end)
        return { 'FINISHED' }

    def generate_a_run_speeds(self, scene, targ, filepath, start_frame = 0, end_frame = 0):
        os.system("cls")

        targ_obj = scene.objects[targ]

        if targ_obj.type != 'EMPTY':
            self.report({'ERROR_INVALID_INPUT'}, "Target must be an Empty object!")
            return

        old_frame = scene.frame_current

        frame = start_frame

        # erase the file first
        file = open(filepath, 'w').close()

        txt_to_save = ""

        targ_prev_y = 0.0

        for f in range(start_frame, end_frame + 1):
            scene.frame_set(f)

            targ_cur_y = targ_obj.location.y
            calc_y = targ_cur_y - targ_prev_y

            # fix sign
            calc_y *= -1

            if math.isclose(calc_y, 0):
                calc_y = abs(calc_y)

            # need to divide the distance by tic duration
            tic_duration = 0
            for current_object in scene.objects:
                if current_object.type != 'MESH':
                    continue
                if not current_object.layers[5]:
                    continue
                if current_object.name == "TicDuration":
                    tic_duration = bpy.data.materials[current_object.name].specular_hardness
                    break
            if tic_duration == 0:
                self.report({'ERROR_INVALID_INPUT'}, "No TicDuration found!")
            calc_y /= tic_duration

            # round down
            d = 4
            calc_y = round(calc_y, d)

            scene.update()
            bpy.ops.wm.redraw_timer(type = 'DRAW_WIN_SWAP', iterations = 1)

            targ_prev_y = targ_cur_y

            txt_to_save = ""
            txt_to_save = "A_Run(" + str(calc_y) + ");"
            txt_to_save = txt_to_save + "\n"

            # write to file
            file = open(filepath, 'a')
            file.write(txt_to_save)
            file.close()

        scene.frame_set(old_frame)

    def generate_a_movepos_speeds(self, scene, targ, filepath, start_frame = 0, end_frame = 0):
        if generate_a_movepos == False:
            return

        os.system("cls")

        targ_obj = scene.objects[targ]

        if targ_obj.type != 'EMPTY':
            self.report({'ERROR_INVALID_INPUT'}, "Target must be an Empty object!")
            return

        old_frame = scene.frame_current

        frame = start_frame

        # erase the file first
        #file = open(filepath, 'w').close()
        file = open(filepath, 'a')
        file.write("\n")
        file.close()

        txt_to_save = ""

        targ_prev_y = 0.0
        targ_prev_x = 0.0
        targ_prev_z = 0.0

        for f in range(start_frame, end_frame + 1):
            scene.frame_set(f)

            targ_cur_y = targ_obj.location.y
            calc_y = targ_cur_y - targ_prev_y
            targ_cur_x = targ_obj.location.x
            calc_x = targ_cur_x - targ_prev_x
            targ_cur_z = targ_obj.location.z
            calc_z = targ_cur_z - targ_prev_z

            # fix sign
            calc_y *= -1
            #calc_x *= -1
            #calc_z *= -1

            if math.isclose(calc_y, 0):
                calc_y = abs(calc_y)
            if math.isclose(calc_x, 0):
                calc_x = abs(calc_x)
            if math.isclose(calc_z, 0):
                calc_z = abs(calc_z)

            # need to divide the distance by tic duration
            tic_duration = 0
            for current_object in scene.objects:
                if current_object.type != 'MESH':
                    continue
                if not current_object.layers[5]:
                    continue
                if current_object.name == "TicDuration":
                    tic_duration = bpy.data.materials[current_object.name].specular_hardness
                    break
            if tic_duration == 0:
                self.report({'ERROR_INVALID_INPUT'}, "No TicDuration found!")
            calc_y /= tic_duration
            calc_x /= tic_duration
            calc_z /= tic_duration

            # round down
            d = 4
            calc_y = round(calc_y, d)
            calc_x = round(calc_x, d)
            calc_z = round(calc_z, d)

            scene.update()
            bpy.ops.wm.redraw_timer(type = 'DRAW_WIN_SWAP', iterations = 1)

            targ_prev_y = targ_cur_y
            targ_prev_x = targ_cur_x
            targ_prev_z = targ_cur_z

            txt_to_save = ""
            txt_to_save = txt_to_save + "A_MovePos(" + str(calc_y) + ", " +str(calc_x) + ", " + str(calc_z) + ");"
            txt_to_save = txt_to_save + "\n"

            # write to file
            file = open(filepath, 'a')
            file.write(txt_to_save)
            file.close()

        scene.frame_set(old_frame)


class DisdainToolsGenScriptsOperator(bpy.types.Operator):
    bl_idname = "render.disdaintools_genscripts_operator"
    bl_label = "DisdainToolsGenScripts Operator"
    bl_options = { 'REGISTER' }

    def execute(self, context):
        os.system("cls")

        # erase the file first
        file = open(context.scene.disdaintools.filepath_scripts, 'w').close()

        self.genscripts_zscript_operator(context.scene, context.scene.disdaintools.filepath_scripts, context.scene.frame_start, context.scene.frame_end)
        self.genscripts_modeldef_operator(context.scene, context.scene.disdaintools.filepath_scripts, context.scene.frame_start, context.scene.frame_end)
        self.genscripts_animspec_operator(context.scene, context.scene.disdaintools.filepath_scripts, context.scene.frame_start, context.scene.frame_end)
        self.genscripts_initanimdata_operator(context.scene, context.scene.disdaintools.filepath_scripts, context.scene.frame_start, context.scene.frame_end)

        return { 'FINISHED' }

    def genscripts_zscript_operator(self, scene, filepath, start_frame = 0, end_frame = 0):
        print("Generating ZScript...")

        txt_to_save = "// ZSCRIPT //////////"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "\n"

        frames = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        total_frames = len(frames)

        old_frame = scene.frame_current
        frame = start_frame

        old_state_label = ""

        current_sprite = 0
        current_state = 0

        for f in range(start_frame, end_frame + 1):
            scene.frame_set(f)

            # skip the default frame
            if f == 0:
                continue

            new_state_label = ""

            for k, m in scene.timeline_markers.items():
                if (m.frame == f):
                    if old_state_label != m.name:
                        new_state_label = m.name
                    if old_state_label != new_state_label:
                        old_state_label = new_state_label

            # special parsing
            is_directive = False
            is_infinite_tic = False
            tic_duration = 1
            if new_state_label:
                if new_state_label[0] == ':':
                    is_directive = True
                elif new_state_label[0] == '-':
                    is_directive = True
                    is_infinite_tic = True

            # look for special meshes (only on layer 5)
            functions = ""
            for current_object in scene.objects:
                if current_object.type != 'MESH':
                    continue
                if not current_object.layers[5]:
                    continue
                # TicDuration mesh
                if current_object.name == "TicDuration":
                    tic_duration = bpy.data.materials[current_object.name].specular_hardness
                # Function mesh
                elif current_object.name == "ScriptFunctions":
                    for current_material in current_object.data.materials:
                        if current_material.specular_intensity > 0:
                            functions = current_material.name
                            break

            # write state label
            if new_state_label and is_directive == False and is_infinite_tic == False:
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "%s:" % (new_state_label)
                txt_to_save = txt_to_save + "\n"

                # write A_SetAnim call
                if use_decoupled_anim == True:
                    txt_to_save = txt_to_save + "\t"
                    txt_to_save = txt_to_save + "\t"
                    txt_to_save = txt_to_save + "%04d %s %d " % (0, frames[0], 0)
                    #txt_to_save = txt_to_save + "SetAnimation('%s', %f);" % (new_state_label, 35 / tic_duration)
                    txt_to_save = txt_to_save + "A_SetAnim('%s');" % (new_state_label)
                    txt_to_save = txt_to_save + "\n"

                if f > 1:
                    current_sprite += 1
                current_state = 0

            if current_state >= total_frames:
                current_sprite += 1
                current_state = 0

            sprite_frame = current_sprite
            state_frame = frames[(current_state) % total_frames]

            # force all States to be 0000 A if using decoupled animation
            if use_decoupled_anim == True:
                sprite_frame = 0
                state_frame = frames[0]

            # write state
            state_tics = -1 if is_infinite_tic else tic_duration
            txt_to_save = txt_to_save + "\t"
            txt_to_save = txt_to_save + "\t"
            txt_to_save = txt_to_save + "%04d %s %d" % (sprite_frame, state_frame, state_tics)
            if functions:
                txt_to_save = txt_to_save + " " + functions
            else:
                txt_to_save = txt_to_save + ";"
            txt_to_save = txt_to_save + "\n"

            # parse directive
            if new_state_label and is_directive == True:
                new_state_label = new_state_label[1:]
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "%s;\n" % (new_state_label)

            current_state += 1

        file = open(filepath, 'a')
        file.write(txt_to_save)
        file.close()

        scene.frame_set(old_frame)

    def genscripts_modeldef_operator(self, scene, filepath, start_frame = 0, end_frame = 0):
        if use_decoupled_anim == True:
            return

        print("Generating MODELDEF...")

        txt_to_save = ""
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "// MODELDEF //////////"
        txt_to_save = txt_to_save + "\n"

        frames = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        total_frames = len(frames)

        old_frame = scene.frame_current
        frame = start_frame

        old_state_label = ""

        current_sprite = 0
        current_state = 0

        modeldef_anim_name = ""
        frame_to_write = 0

        for f in range(start_frame, end_frame + 1):
            scene.frame_set(f)

            # skip Ref
            if f == 0:
                continue

            new_state_label = ""

            for k, m in scene.timeline_markers.items():
                if (m.frame == f):
                    if old_state_label != m.name:
                        new_state_label = m.name
                    if old_state_label != new_state_label:
                        old_state_label = new_state_label

                    if use_anim_clips == True:
                        # write iqm frame name for the MODELDEF
                        if new_state_label[0] != ':' and new_state_label[0] != '-':
                            modeldef_anim_name = m.name

            # skip directives
            if new_state_label:
                if new_state_label[0] == ':' or new_state_label[0] == '-':
                    new_state_label = ""

            if new_state_label:
                #print("// %s" % (new_state_label))
                txt_to_save = txt_to_save + "\n"
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "// %s" % (new_state_label)
                txt_to_save = txt_to_save + "\n"
                if f > 1:
                    current_sprite += 1
                current_state = 0

            if current_state >= total_frames:
                current_sprite += 1
                current_state = 0

            sprite_frame = current_sprite
            state_frame = frames[(current_state) % total_frames]

            if use_anim_clips == True:
                if new_state_label:
                    frame_to_write = 0
                else:
                    frame_to_write += 1

            #print("FrameIndex %04d %s 0 %d" % (sprite_frame, state_frame, f))
            txt_to_save = txt_to_save + "\t"
            if use_anim_clips == False:
                txt_to_save = txt_to_save + "FrameIndex %04d %s 0 %d" % (sprite_frame, state_frame, f)
            else:
                txt_to_save = txt_to_save + "Frame %04d %s 0 \"%s:%d\"" % (sprite_frame, state_frame, modeldef_anim_name, frame_to_write)
            txt_to_save = txt_to_save + "\n"

            current_state += 1

        file = open(filepath, 'a')
        file.write(txt_to_save)
        file.close()

        scene.frame_set(old_frame)

    def genscripts_animspec_operator(self, scene, filepath, start_frame = 0, end_frame = 0):
        print("Generating animspec...")

        txt_to_save = ""
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "// ACTIONS //////////"
        txt_to_save = txt_to_save + "\n"

        old_frame = scene.frame_current
        frame = start_frame

        old_state_label = ""

        for f in range(start_frame, end_frame + 1):
            scene.frame_set(f)

            if f == 0:
                continue

            new_state_label = ""

            for k, m in scene.timeline_markers.items():
                if (m.frame == f):
                    if old_state_label != m.name:
                        new_state_label = m.name
                    if old_state_label != new_state_label:
                        old_state_label = new_state_label

            if new_state_label:
                if new_state_label[0] == ':' or new_state_label[0] == '-':
                    new_state_label = ""

            if new_state_label:
                txt_to_save = txt_to_save + "%s," % (new_state_label)

        # remove last comma
        txt_to_save = txt_to_save[:-1]

        txt_to_save = txt_to_save + "\n"

        file = open(filepath, 'a')
        file.write(txt_to_save)
        file.close()

        scene.frame_set(old_frame)

    def genscripts_initanimdata_operator(self, scene, filepath, start_frame = 0, end_frame = 0):
        if use_decoupled_anim == False:
            return

        print("Generating InitAnimData...")

        txt_to_save = "\t// "

        tic_duration = 0
        anim_state_name = ""
        anim_state_names = []
        anim_state_durations = []

        old_frame = scene.frame_current
        frame = start_frame

        old_state_label = ""

        for f in range(start_frame, end_frame + 1):
            scene.frame_set(f)

            if f == 0:
                continue

            new_state_label = ""

            for k, m in scene.timeline_markers.items():
                if (m.frame == f):
                    if old_state_label != m.name:
                        new_state_label = m.name
                    if old_state_label != new_state_label:
                        old_state_label = new_state_label

            if new_state_label:
                if new_state_label[0] == ':' or new_state_label[0] == '-':
                    new_state_label = ""

            if new_state_label:
                txt_to_save = txt_to_save + "%s" % (new_state_label)

                if animspec_comment_embed_fps:
                    tic_duration_to_add = 0
                    for current_object in scene.objects:
                        if current_object.type != 'MESH':
                            continue
                        if not current_object.layers[5]:
                            continue
                        if current_object.name == "TicDuration":
                            tic_duration_to_add = bpy.data.materials[current_object.name].specular_hardness
                            break
                    current_action_fps = round((35.0 / tic_duration_to_add), 4)
                    txt_to_save = txt_to_save + ":::%.4f" % (current_action_fps)

                txt_to_save = txt_to_save + ","
                anim_state_names.append(new_state_label)

                tic_duration_to_add = 0
                for current_object in scene.objects:
                    if current_object.type != 'MESH':
                        continue
                    if not current_object.layers[5]:
                        continue
                    if current_object.name == "TicDuration":
                        tic_duration_to_add = bpy.data.materials[current_object.name].specular_hardness
                        break
                anim_state_durations.append(tic_duration_to_add)

        # remove last comma
        txt_to_save = txt_to_save[:-1]

        # save the text as a comment to be pasted later in the IQM export dialog
        animspec_comment = txt_to_save
        txt_to_save = ""

        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "//==========================================================================="
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "//"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "// ANIMATION DATA (Generated from DisdainTools, do not edit by hand)"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "//"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "//==========================================================================="
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "override void InitAnimData(void)"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "{"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + animspec_comment
        txt_to_save = txt_to_save + "\n"

        cnt = 0
        for x in anim_state_names:
            anim_state_name = x
            tic_duration = anim_state_durations[cnt]
            txt_to_save = txt_to_save + "\t" + "SetAnimData('" + anim_state_name + "', " + "%d" % (tic_duration) + ");"
            txt_to_save = txt_to_save + "\n"
            cnt += 1

        txt_to_save = txt_to_save + "}"
        txt_to_save = txt_to_save + "\n"
        txt_to_save = txt_to_save + "\n"

        file = open(filepath, 'a')
        file.write(txt_to_save)
        file.close()

        scene.frame_set(old_frame)


class DisdainToolsPanel(bpy.types.Panel):
    bl_idname = 'disdaintools_panel'
    bl_label = 'DisdainTools'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        l = self.layout
        framerow = l.row()
        props = context.scene.disdaintools

        # OUTPUT A_RUN SPEEDS
        l.column().prop_search(props, "targ", context.scene, "objects", icon = 'OBJECT_DATA', text = "Target object")
        if props.targ not in context.scene.objects:
            l.column().label("Invalid target object '%s'!" % (props.targ), icon = 'ERROR')
        l.row().prop(props, "filepath_arunspeeds", text = "Output path")
        row = l.row()
        row.operator("render.disdaintools_genarunspeeds_operator", text = "Generate A_Run() Speeds", icon = 'TEXT')
        row = l.row()

        # OUTPUT SCRIPTS
        l.row().prop(props, "filepath_scripts", text = "Output path")
        row = l.row()
        row.operator("render.disdaintools_genscripts_operator", text = "Generate Animation Scripts", icon = 'TEXT')


def register():
    bpy.utils.register_class(DisdainToolsGenARunSpeedsOperator)
    bpy.utils.register_class(DisdainToolsGenScriptsOperator)
    bpy.utils.register_class(DisdainToolsPanel)
    bpy.utils.register_class(DisdainToolsSettings)

    bpy.types.Scene.disdaintools = bpy.props.PointerProperty(type = DisdainToolsSettings)


def unregister():
    bpy.utils.unregister_class(DisdainToolsGenARunSpeedsOperator)
    bpy.utils.unregister_class(DisdainToolsGenScriptsOperator)
    bpy.utils.unregister_class(DisdainToolsPanel)
    bpy.utils.unregister_class(DisdainToolsSettings)
    del bpy.types.Scene.disdaintools


if __name__ == "__main__":
    register()
