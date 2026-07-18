import time
from uuid import uuid4
from bpy.types import Operator
import bpy
from ..utils.getters import get_wm_props
from random import randint


class Task:
    def __init__(self, total: int) -> None:
        self.total = total
        self.id = uuid4().hex
        self.register()

    def register(self):
        wm_props = get_wm_props(bpy.context)
        slow_tasks = wm_props.slow_task.tasks
        task = slow_tasks.add()
        task.name = self.id

    def unregister(self):
        wm_props = get_wm_props(bpy.context)
        slow_tasks = wm_props.slow_task.tasks
        i = slow_tasks.find(self.id)
        slow_tasks.remove(i)

    @property
    def task(self):
        wm_props = get_wm_props(bpy.context)
        slow_tasks = wm_props.slow_task.tasks
        return slow_tasks[self.id]

    def refresh(self):
        bpy.ops.gscatter.show_progress("INVOKE_DEFAULT")
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

    def set_progress(self, progress: int):
        progress = int((progress / self.total) * 100)
        self.task.progress = progress

    def set_progress_text(self, text: str):
        self.task.progress_text = text


class StartSlowTask(object):
    """Create and manage a slow tasks. Displays a progress dialog"""

    running_task: bool = False
    tasks = []

    def __init__(self, task_name: str, total: int) -> None:
        self.name = task_name
        self.total = total
        self.task = None

    def __enter__(self):
        if not StartSlowTask.running_task:
            StartSlowTask.running_task = True
            self.show_progress()
            task = Task(self.total)
            self.task = task
            StartSlowTask.tasks.append(task)
            return task
        else:
            task = Task(self.total)
            self.task = task
            StartSlowTask.tasks.append(task)
            return task

    def show_progress(self):
        bpy.ops.gscatter.show_progress("INVOKE_DEFAULT")

    def __exit__(self, *args):
        self.task.unregister()
        StartSlowTask.tasks.remove(self.task)
        if len(StartSlowTask.tasks) <= 0:
            StartSlowTask.running_task = False
            SlowTaskPanel.cx = None
            SlowTaskPanel.cy = None


class SlowTaskPanel(Operator):
    bl_idname = "gscatter.show_progress"
    bl_label = "Show Progress"

    cx = None
    cy = None

    def draw(self, context):
        layout = self.layout
        wm_props = get_wm_props(context)
        tasks = wm_props.slow_task.tasks
        if len(tasks) == 0:
            return

        layout.separator()

        col = layout.column()
        col.prop(wm_props.slow_task.tasks[0], "progress", text="", slider=True)
        for text in wm_props.slow_task.tasks[0].progress_text.split("\n"):
            col.label(text=text)
        col.separator()

        for task in tasks[1:]:
            col = layout.column()
            progress_col = col.column()
            progress_col.scale_y = 0.7
            progress_col.prop(task, "progress", text="", slider=True)
            for text in task.progress_text.split("\n"):
                col.label(text=text)
            col.separator()

    def invoke(self, context, event):
        mouse_x = event.mouse_x
        mouse_y = event.mouse_y

        def reset_mouse():
            context.window.cursor_warp(mouse_x, mouse_y)

        try:
            if SlowTaskPanel.cx is None:
                region = context.region

                SlowTaskPanel.cx = region.width // 2 + region.x
                SlowTaskPanel.cy = region.height // 2 + region.y

                context.window.cursor_warp(
                    SlowTaskPanel.cx - 150, SlowTaskPanel.cy + 150
                )
                bpy.app.timers.register(reset_mouse, first_interval=0.1)
        except Exception:
            pass
        return context.window_manager.invoke_popup(self)

    def execute(self, context):
        return {"FINISHED"}


class SampleSlowTask(Operator):
    bl_idname = "gscatter.start_slow_task"
    bl_label = "Start Slow Task"

    def execute(self, context):
        main_total = randint(1, 20)
        with StartSlowTask("Main task", main_total) as slow_task:
            for i in range(main_total):
                slow_task.set_progress(i)
                slow_task.set_progress_text(f"Main task progress: {i}/{main_total}")
                slow_task.refresh()

                total = randint(1, 20)
                with StartSlowTask("Child task", total) as child_task:
                    for i in range(total):
                        child_task.set_progress(i)
                        child_task.set_progress_text(f"Child task: {i}/{total}")
                        child_task.refresh()
                        an_total = randint(1, 20)
                        with StartSlowTask("Child task", an_total) as t:
                            for i in range(an_total):
                                t.set_progress(i)
                                t.set_progress_text(f"Child task: {i}/{an_total}")
                                t.refresh()
                                time.sleep(0.1)

        return {"FINISHED"}


classes = (SlowTaskPanel, SampleSlowTask)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
