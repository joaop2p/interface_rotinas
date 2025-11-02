
from typing import List, Optional
import flet as ft


class IconSelectorMenu(ft.Container):
	"""
    Widget para seleção de ícones com filtro e paginação.
	"""

	def __init__(self, page_size: int = 30, height: int = 280, ref: Optional[ft.Ref] = None):
		super().__init__()
		self.selected_icon: Optional[str] = None
		self.ref = ref
		# Configurações
		self._page_size: int = max(1, page_size)
		self._height: int = height

		# Estado
		self._icons_all: List[str] = self._get_all_icons()
		self._icons_filtered: List[str] = list(self._icons_all)
		self._page_index: int = 0


		# Referências de UI
		self._filter_field: Optional[ft.TextField] = None
		self._icons_grid: Optional[ft.GridView] = None
		self._status_text: Optional[ft.Text] = None

		# Monta o conteúdo do container
		self._build_ui()
		self._update_window()

	# ----------------- Dados -----------------
	def _get_all_icons(self) -> List[str]:
		icons: List[str] = []
		for attr in dir(ft.Icons):
			if not attr.startswith("_"):
				value = getattr(ft.Icons, attr)
				if isinstance(value, str):
					icons.append(value)
		return icons

	def _apply_filter(self, value: str):
		needle = (value or "").strip().lower()
		if needle:
			self._icons_filtered = [n for n in self._icons_all if needle in n.lower()]
		else:
			self._icons_filtered = self._icons_all
		self._page_index = 0
		self._update_window()

	# ----------------- Navegação -----------------
	def _next_page(self, e=None):
		total = len(self._icons_filtered)
		if total == 0:
			return
		max_pages = (total + self._page_size - 1) // self._page_size
		if self._page_index < max_pages - 1:
			self._page_index += 1
			self._update_window()

	def _prev_page(self, e=None):
		if self._page_index > 0:
			self._page_index -= 1
			self._update_window()

	# ----------------- UI -----------------
	def _build_ui(self):
		self._filter_field = ft.TextField(
			label="Filtrar ícones (por nome)",
			hint_text="Ex.: add, arrow, home...",
			dense=True,
			width=360,
			on_change=lambda e: self._apply_filter(e.control.value),
		)

		# Grid responsivo para os ícones
		self._icons_grid = ft.GridView(
			expand=True,
			runs_count=0,            # 0 = calcula automaticamente com base em max_extent
			max_extent=80,          # largura máx. por tile (ajuste conforme preferir)
			child_aspect_ratio=1.0,
			spacing=8,
			run_spacing=8,
		)
		self._status_text = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT)

		# Visualizador com rolagem contendo grid e barra de navegação
		viewer = ft.Container(
			height=self._height,
			width=400,
			content=ft.Column(
				controls=[
					# Grid ocupa o espaço disponível
					ft.Container(expand=True, content=self._icons_grid),
					# Barra de navegação
					ft.Row(
						controls=[
							ft.TextButton("Anterior", on_click=self._prev_page),
							ft.TextButton("Próximo", on_click=self._next_page),
							ft.Container(expand=True),
							self._status_text,
						],
						alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
					),
				],
				spacing=10,
			),
			padding=0,
		)

		# Monta o container raiz (este próprio objeto)
		self.padding = 0
		self.content = ft.Column(
			controls=[
				self._filter_field,
				viewer,
			],
			spacing=10,
		)

	def _set_selected_icon(self, icon_name: str):
		self.selected_icon = icon_name

	def _update_window(self):
		if not self._icons_grid or not self._status_text:
			return

		total = len(self._icons_filtered)
		start = self._page_index * self._page_size
		end = min(total, start + self._page_size)
		if start >= total and total > 0:
			# reajuste se filtro reduziu muito
			self._page_index = 0
			start = 0
			end = min(total, self._page_size)

		names_slice = self._icons_filtered[start:end]
		# Renderiza somente os ícones da janela atual
		self._icons_grid.controls = [
			ft.Container(content=ft.Icon(name=n, size=22), tooltip=n, padding=6, on_click=lambda _, n=n: self._set_selected_icon(n))
			for n in names_slice
		]

		self._status_text.value = (
			f"Mostrando {start + 1}-{end} de {total}" if total > 0 else "Nenhum ícone encontrado"
		)

		try:
			self.update()
		except Exception:
			pass

class IconSelector(ft.AlertDialog):
	selector: IconSelectorMenu

	def __init__(
		self,
		page_size: int = 30,
		height: int = 280,
		ref: Optional[ft.Ref] = None,
		on_accept: Optional[callable] = None,
	):
		self.selector = IconSelectorMenu(page_size=page_size, height=height, ref=ref)
		self.selected_icon_display = ft.Icon(name=ft.Icons.HELP, size=20)
		self._on_accept = on_accept
		super().__init__(
			title=ft.Text("Selecionar Ícone"),
			content=ft.Column(
				controls=[
					self.selector,
					ft.Container(
						content=ft.Row(
							controls=[
								ft.Text("Ícone selecionado:"),
								self.selected_icon_display,
							],
						)
					)
				]
			),
			actions=[
				ft.ElevatedButton("Aceitar", on_click=self._accept_click),
				ft.ElevatedButton("Cancelar", on_click=self._close),
			],
			modal=True,
		)

		# Override do método _set_selected_icon para atualizar o display
		original_set_selected = self.selector._set_selected_icon

		def update_selected_icon(icon_name: str):
			original_set_selected(icon_name)
			self.selected_icon_display.name = icon_name
			self.selected_icon_display.update()

		self.selector._set_selected_icon = update_selected_icon

	def _accept_click(self, e: ft.ControlEvent):
		if self._on_accept:
			try:
				self._on_accept(self.selector.selected_icon)
			except Exception:
				pass
		self._close(e)

	def _close(self, e: ft.ControlEvent):
		self.open = False
		self.update()

