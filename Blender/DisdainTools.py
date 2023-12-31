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

class DisdainToolsSettings(bpy.types.PropertyGroup):
    targ = StringProperty\
    (
        name = "Target object",
        description = """The Empty object to use for A_Run calculation""",
        default = ""
    )

    filepath_arunspeeds = StringProperty\
    (
        name = "ZScript output path",
        description = """Where to save the ZScript""",
        default = "",
        subtype = 'FILE_PATH'
    )

    filepath_scripts = StringProperty\
    (
        name = "ZScript and MODELDEF output path",
        description = """Where to save the ZScript and MODELDEF""",
        default = "",
        subtype = 'FILE_PATH'
    )


class DisdainToolsGenARunSpeedsOperator(bpy.types.Operator):
    bl_idname = "render.disdaintools_genarunspeeds_operator"
    bl_label = "DisdainToolsGenARunSpeeds Operator"
    bl_options = { 'REGISTER' }

    def execute(self, context):
        self.generate_a_run_speeds(context.scene, context.scene.disdaintools.targ, context.scene.disdaintools.filepath_arunspeeds, context.scene.frame_start, context.scene.frame_end)
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
            calc_y = abs(calc_y)

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
            #txt_to_save = txt_to_save + "\n"
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
        return { 'FINISHED' }

    def genscripts_zscript_operator(self, scene, filepath, start_frame = 0, end_frame = 0):
        print("generating zscript")

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

            # look for special stuff (functions, tic duration, etc (only on layer 5))
            functions = ""
            for current_object in scene.objects:
                if current_object.type != 'EMPTY':
                    continue
                if not current_object.layers[5]:
                    continue
                # set tic duration
                if bpy.data.objects[current_object.name].get('TicDuration') is not None:
                    tic_duration = bpy.data.objects[current_object.name]['TicDuration']
                if current_object.hide:
                    continue
                if bpy.data.objects[current_object.name].get('DisdainFunctions') is not None:
                    functions = bpy.data.objects[current_object.name]['DisdainFunctions']

            # write state label
            if new_state_label and is_directive == False and is_infinite_tic == False:
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "%s:" % (new_state_label)
                txt_to_save = txt_to_save + "\n"
                """
                # write SetAnimation call and also the framerate
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "\t"
                txt_to_save = txt_to_save + "TNT1 A 0 "
                txt_to_save = txt_to_save + "SetAnimation(\"%s\", %f);" % (new_state_label, 35 / tic_duration)
                txt_to_save = txt_to_save + "\n"
                """
                if f > 1:
                    current_sprite += 1
                current_state = 0

            if current_state >= total_frames:
                current_sprite += 1
                current_state = 0

            sprite_frame = current_sprite
            state_frame = frames[(current_state) % total_frames]

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
        print("generating modeldef")

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

        # set use_anim_clips to True to use per-animation-clip workflow
        # False if using old-style workflow where all of the animations is a single giant and long timeline
        use_anim_clips = True
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
        print("generating animspec")

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
        row.operator("render.disdaintools_genscripts_operator", text = "Generate Scripts", icon = 'TEXT')


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
