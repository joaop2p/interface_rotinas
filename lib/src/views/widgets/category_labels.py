from flet import Container, Icon, Row, Text, Animation, AnimationCurve, ControlEvent, FontWeight, TextStyle
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
        elif self.content.controls[1] is None or not isinstance(self.content.controls[1], Text):
            return
        self.content.controls[1].style = TextStyle(weight=FontWeight.BOLD if selected else FontWeight.NORMAL)
        self.content.controls[1].update()



    def __init__(self, category: Category, **kwargs):
        super().__init__(**kwargs)
        self.category = category
        # self.bgcolor = "#E0E0E0"
        # self.expand = True
        self.animate_scale = Animation(duration=300, curve=AnimationCurve.EASE_IN_OUT_QUAD)
        self.on_hover = self._animation
        self.content = Row(
            controls=[
                Icon(name=category.icon),
                Text(category.category_name),
            ]
        )