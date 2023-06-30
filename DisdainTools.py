# DisdainTools
# Written by Nash Muhandes for DISDAIN
# https://store.steampowered.com/app/2113270/DISDAIN/
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
		"version" : (1, 2, 0),
		"blender" : (2, 7, 9),
		"location" : "Render",
		"description" : "",
		"warning" : "",
		"wiki_url" : "",
		"tracker_url" : "",
		"category" : "Render",
	}


class DisdainToolsSettings(bpy.types.PropertyGroup):
	targ = StringProperty (
		name = "Target object",
		description = """The Empty object to use for A_Run calculation""",
		default = ""
	)

	filepath = StringProperty (
		name = "ZScript output path",
		description = """Where to save the ZScript""",
		default = "",
		subtype = 'FILE_PATH'
	)


class DisdainToolsOperator(bpy.types.Operator):
	bl_idname = "render.disdaintools_operator"
	bl_label = "DisdainTools Operator"
	bl_options = {'REGISTER'}

	def execute(self, context):
		self.generate_a_run_speeds(
			context.scene,
			context.scene.disdaintools.targ,
			context.scene.disdaintools.filepath,
			context.scene.frame_start,
			context.scene.frame_end
		)
		return {'FINISHED'}

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

		to_save = ""

		targ_prev_y = 0.0

		for f in range(start_frame, end_frame + 1):
			scene.frame_set(f)

			targ_cur_y = targ_obj.location.y
			calc_y = targ_cur_y - targ_prev_y

			scene.update()
			bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

			targ_prev_y = targ_cur_y

			to_save = ""
			to_save = "A_Run(" + str(calc_y) + ");"
			to_save = to_save + "\n"

			# write to file
			file = open(filepath, 'a')
			#to_save = to_save + "\n"
			file.write(to_save)
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

		l.column().prop_search(props, "targ", context.scene, "objects",\
				icon='OBJECT_DATA', text="Target object")

		if props.targ not in context.scene.objects:
			l.column().label("Invalid target object '%s'!" % (props.targ),
			icon='ERROR')

		l.row().prop(props, "filepath", text="Output path")
		row = l.row()
		row.operator("render.disdaintools_operator", text="Generate A_Run() Speeds", icon='RENDER_ANIMATION')


def register():
	bpy.utils.register_class(DisdainToolsOperator)
	bpy.utils.register_class(DisdainToolsPanel)
	bpy.utils.register_class(DisdainToolsSettings)

	bpy.types.Scene.disdaintools = bpy.props.PointerProperty(type=DisdainToolsSettings)


def unregister():
	bpy.utils.unregister_class(DisdainToolsOperator)
	bpy.utils.unregister_class(DisdainToolsPanel)
	bpy.utils.unregister_class(DisdainToolsSettings)
	del bpy.types.Scene.disdaintools


if __name__ == "__main__":
	register()
