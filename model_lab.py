"""
Model Lab - 三维模型查看器
支持 STL / OBJ / PLY / GLTF / GLB / OFF / STEP 格式
"""
import math
import multiprocessing as mp
from pathlib import Path
from nicegui import app, ui, events

_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  html, body { margin: 0; padding: 0; overflow: hidden; background: #0a0e14; }
  .nicegui-content { background: #0a0e14 !important; }
  .q-header {
    background: linear-gradient(90deg, #0d1117 0%, #111827 100%) !important;
    border-bottom: 1px solid #00d4ff33;
    box-shadow: 0 1px 12px #00d4ff22;
  }
  .q-footer {
    background: #0d1117 !important;
    border-top: 1px solid #1e2a3a;
  }
  .toolbar-btn {
    color: #7eb8d4 !important;
    font-size: 11px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.5px;
    border: 1px solid transparent !important;
    border-radius: 3px !important;
    transition: all 0.15s ease;
  }
  .toolbar-btn .q-icon { color: #7eb8d4 !important; font-size: 16px !important; }
  .toolbar-btn:hover {
    background: #00d4ff11 !important;
    border-color: #00d4ff44 !important;
    color: #00d4ff !important;
  }
  .toolbar-btn:hover .q-icon { color: #00d4ff !important; }
  .app-title {
    color: #00d4ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    letter-spacing: 3px;
    text-shadow: 0 0 12px #00d4ff88;
  }
  .status-bar {
    color: #3a6a7a !important;
    font-size: 11px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.5px;
  }
  .divider { width: 1px; height: 20px; background: #1e3a4a; margin: 0 4px; }
</style>
"""

# ---- 目录配置 ----
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

for name, path in [("stl", BASE_DIR / "STL"),
                   ("output", OUTPUT_DIR),
                   ("cad_stl", BASE_DIR / "cad_parts" / "STL")]:
    if path.exists():
        app.add_static_files(f"/{name}", str(path))

# ---- 全局状态 ----
current_model_name: str = ""
current_mesh_data: bytes | None = None
_default_camera = {"x": 7.5, "y": 100, "z": 150,
                   "lx": 7.5, "ly": 20, "lz": 30}


def _compute_model_info(stl_path: str) -> dict:
    """读取 STL 文件，返回 center, max_extent 用于相机定位。"""
    import trimesh
    mesh = trimesh.load_mesh(stl_path)
    b = mesh.bounds  # [[min_x,min_y,min_z], [max_x,max_y,max_z]]
    size = b[1] - b[0]
    center = (b[0] + b[1]) / 2
    max_extent = float(size.max())
    return {
        "center": (float(center[0]), float(center[1]), float(center[2])),
        "max_extent": max_extent,
    }


def _nice_step(extent: float) -> float:
    """根据模型尺寸计算合适的网格步长 (1, 2, 5, 10, 20, 50...)。"""
    rough = extent / 8
    exp = 10 ** math.floor(math.log10(rough))
    if rough / exp < 2:
        return exp
    if rough / exp < 5:
        return 2 * exp
    return 5 * exp


def _place_on_ground(mesh) -> None:
    """XY 居中，Z 方向底面贴到 z=0（放在地上）。"""
    center = (mesh.bounds[0] + mesh.bounds[1]) / 2
    mesh.apply_translation([-center[0], -center[1], -mesh.bounds[0][2]])


def _build_scene_helpers(scene, half: float, step: float):
    """Z=0 平面网格 + XYZ 坐标轴（NiceGUI Z-up）。"""
    h = math.ceil(half / step) * step
    s = step

    with scene.group():
        # 网格在 Z=0 平面（XY 平面）
        x = -h
        while x <= h + s * 0.01:
            major = abs(round(x / s) % 5) == 0
            scene.line([x, -h, 0], [x, h, 0]).material("#3a3a3a" if major else "#222222")
            x = round(x + s, 10)
        y = -h
        while y <= h + s * 0.01:
            major = abs(round(y / s) % 5) == 0
            scene.line([-h, y, 0], [h, y, 0]).material("#3a3a3a" if major else "#222222")
            y = round(y + s, 10)

        axis_len = h * 0.6
        scene.line([0, 0, 0], [axis_len, 0, 0]).material("#cc3333")   # X 红
        scene.line([0, 0, 0], [0, axis_len, 0]).material("#33cc33")   # Y 绿
        scene.line([0, 0, 0], [0, 0, axis_len]).material("#3366cc")   # Z 蓝（朝上）

        d = s * 0.3
        scene.line([-d, 0, 0], [d, 0, 0]).material("#ffffff")
        scene.line([0, -d, 0], [0, d, 0]).material("#ffffff")


# ---- 主页 ----
@ui.page("/")
def main_page():
    global current_model_name, current_mesh_data, _default_camera

    ui.query(".nicegui-content").classes("flex flex-col h-screen")
    ui.add_head_html(_STYLE + """
    <script>
      window.addEventListener("mousedown", function(e) {
        if (e.button === 1) e.preventDefault();
      }, {passive: false});
      window.addEventListener("auxclick", function(e) {
        if (e.button === 1) e.preventDefault();
      }, {passive: false});
    </script>
    """)

    # 默认相机：Z-up，从斜上方看原点
    _default_camera.update({"x": 120, "y": 120, "z": 150, "lx": 0, "ly": 0, "lz": 0})
    cam = _default_camera

    # -- 底栏 --
    with ui.footer().classes("items-center px-4 py-1"):
        status_label = ui.label("就绪 | 未加载模型").classes("status-bar")

    # -- 3D 场景 --
    with ui.element("div").classes("flex-1 w-full min-h-0"):
        scene = ui.scene(grid=False).classes("w-full h-full")

    # -- 上传控件 --
    upload = ui.upload(
        on_upload=lambda e: handle_upload(e, scene, status_label),
        auto_upload=True,
        multiple=False,
    ).props("accept=.stl,.obj,.ply,.gltf,.glb,.off,.stp,.step,.sldprt")
    upload.classes("hidden")

    # ---- 功能函数 ----
    def clear_scene():
        global current_model_name, current_mesh_data
        with scene:
            scene.delete_objects(lambda obj: True)
        current_model_name = ""
        current_mesh_data = None
        _default_camera.update({"x": 120, "y": 120, "z": 150, "lx": 0, "ly": 0, "lz": 0})
        _build_scene_helpers(scene, 100, 10)
        status_label.set_text("就绪 | 未加载模型")

    def reset_view():
        scene.move_camera(
            x=cam["x"], y=cam["y"], z=cam["z"],
            look_at_x=cam["lx"], look_at_y=cam["ly"], look_at_z=cam["lz"],
        )

    # -- 顶栏 --
    with ui.header(elevated=True).classes("items-center justify-between px-4 py-1"):
        ui.label("MODEL LAB").classes("app-title")
        with ui.row().classes("gap-1 items-center"):
            ui.button("加载文件", icon="upload_file",
                      on_click=lambda: upload.run_method('pickFiles')).classes("toolbar-btn").props("flat dense")
            ui.element("div").classes("divider")
            ui.button("复位视角", icon="center_focus_strong",
                      on_click=reset_view).classes("toolbar-btn").props("flat dense")
            ui.button("清除", icon="layers_clear",
                      on_click=clear_scene).classes("toolbar-btn").props("flat dense")

    # 启动时显示默认网格（空场景）
    _build_scene_helpers(scene, 100, 10)
    reset_view()


# ---- 文件上传处理 ----
async def handle_upload(e: events.UploadEventArguments, scene, status_label):
    global current_model_name, current_mesh_data, _default_camera

    filename = e.file.name
    ext = Path(filename).suffix.lower()

    if ext == ".sldprt":
        ui.notify(
            "SLDPRT 是 SolidWorks 私有格式，无法直接读取。\n"
            "请从 SolidWorks 导出为 STEP 格式：文件 → 另存为 → STEP",
            type="warning", position="top", timeout=8000,
        )
        return

    content = await e.file.read()
    if not content:
        ui.notify(f"文件为空: {filename}", type="warning", position="top")
        return

    with scene:
        scene.delete_objects(lambda obj: True)

    try:
        out_path = _load_and_convert(content, filename, ext)
    except Exception as err:
        ui.notify(f"加载失败: {err}", type="negative", position="top")
        status_label.set_text(f"错误: {filename}")
        return

    url = f"/output/{out_path.name}"
    with scene:
        obj = scene.stl(url)
        obj.material("#4488ff")

    # 重新计算网格 & 相机（模型已居中到原点）
    try:
        info = _compute_model_info(str(out_path))
        ext_size = info["max_extent"]
        step = _nice_step(ext_size)
        half = step * math.ceil(ext_size / step * 0.8) + step * 4
        _build_scene_helpers(scene, half, step)
        _default_camera.update({
            "x": ext_size * 1.2, "y": ext_size * 1.2, "z": ext_size * 1.5,
            "lx": 0, "ly": 0, "lz": ext_size * 0.3,
        })
        scene.move_camera(
            x=_default_camera["x"], y=_default_camera["y"], z=_default_camera["z"],
            look_at_x=_default_camera["lx"], look_at_y=_default_camera["ly"], look_at_z=_default_camera["lz"],
        )
    except Exception:
        pass  # 网格/相机调整失败不阻塞加载

    current_model_name = filename
    current_mesh_data = content
    status_label.set_text(f"已加载: {filename}")
    ui.notify(f"已加载: {filename}", type="positive", position="top")


# ---- 格式转换核心 ----
def _load_and_convert(content: bytes, filename: str, ext: str) -> Path:
    import trimesh

    out_path = OUTPUT_DIR / f"{Path(filename).stem}.stl"
    temp_in = OUTPUT_DIR / f"_input_{filename}"
    temp_in.write_bytes(content)

    try:
        if ext in (".stp", ".step"):
            return _convert_step(content, filename)

        mesh = trimesh.load_mesh(str(temp_in))
        _place_on_ground(mesh)
        mesh.export(str(out_path), file_type="stl")
        return out_path
    finally:
        if temp_in.exists():
            temp_in.unlink()


def _convert_step(content: bytes, filename: str) -> Path:
    out_path = OUTPUT_DIR / f"{Path(filename).stem}.stl"

    try:
        from OCC.Core.STEPControl import STEPControl_Reader
        from OCC.Core.StlAPI import StlAPI_Writer
        from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh

        temp_in = OUTPUT_DIR / f"_step_{filename}"
        temp_in.write_bytes(content)

        try:
            reader = STEPControl_Reader()
            status = reader.ReadFile(str(temp_in))
            if status != 1:
                raise RuntimeError(f"STEP 读取失败 (status={status})")

            reader.TransferRoot()
            shape = reader.Shape()
            BRepMesh_IncrementalMesh(shape, 0.1)
            writer = StlAPI_Writer()
            writer.SetASCIIMode(False)
            writer.Write(shape, str(out_path))
            return out_path
        finally:
            if temp_in.exists():
                temp_in.unlink()

    except ImportError:
        raise RuntimeError(
            "STEP 支持需要 pythonocc-core。\n"
            "请运行: pip install pythonocc-core"
        )


# ---- 入口 ----
if __name__ in ("__main__", "__mp_main__"):
    mp.freeze_support()
    ui.run(
        native=True,
        window_size=(1200, 800),
        title="Model Lab",
        reload=False,
    )
