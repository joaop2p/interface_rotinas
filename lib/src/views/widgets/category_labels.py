from flet import Container, Icon, Row, Text, Animation, AnimationCurve, ControlEvent, FontWeight, TextStyle, Icons, MainAxisAlignment
from lib.src.models.db.models import Category
from lib.src.views.widgets.message_box import MessageBox

class CategoryLabels(Container):
    category: Category

    def _animation(self, e: ControlEvent) -> None:
        e.control.scale = 1.1 if e.data == "true" else 1.0
        e.control.update()

    def set_selected(self, selected: bool) -> None:
        if self.content is None or not isinstance(self.content, Row):
            return
        control = self.content.controls[0].content.controls[1]
        if control is None or not isinstance(control, Text):
            return
        control.style = TextStyle(weight=FontWeight.BOLD if selected else FontWeight.NORMAL)
        control.update()


    def __init__(self, category: Category, on_delete: callable = None, **kwargs):
        super().__init__(**kwargs)
        self.category = category
        self.animate_scale = Animation(duration=300, curve=AnimationCurve.EASE_IN_OUT_QUAD)
        self.on_hover = self._animation
        self.content = Row(
            alignment=MainAxisAlignment.CENTER,
            spacing=15,
            controls=[
                Container(
                    content=Row(
                        controls=[
                            Icon(name=category.icon, size=20),
                            Text(category.category_name, style=TextStyle(size=14)),
                        ],
                        alignment="center",
                        spacing=8,
                    )
                ),
                Container(
                    on_click=on_delete,
                    content=Icon(name=Icons.CANCEL, size=16)
                ),
            ]
        )