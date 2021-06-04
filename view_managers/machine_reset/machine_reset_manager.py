from models import MeasureUnitType
from views.reset_page import ResetPageView


class ResetPageManager(ResetPageView):
    def __init__(self, footer_btn=""):
        super(ResetPageManager, self).__init__()
        self.__footer_btn_text = "Reset" if len(footer_btn) == 0 else footer_btn

    def get_footer_btn_name(self) -> str:
        return self.__footer_btn_text

    def is_dirty(self) -> bool:
        return False

    def change_measure_mode(self, unit: MeasureUnitType):
        pass
