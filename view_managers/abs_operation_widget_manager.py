from models import MeasureUnitType


class AbstractOperationWidgetManger:
    def change_mode(self, unit: MeasureUnitType):
        raise NotImplementedError('subclasses must override change_mode()!')

    def get_footer_btn_name(self) -> str:
        raise NotImplementedError('subclasses must override get_footer_name()!')

    def destroy_all_operations(self):
        raise NotImplementedError('subclasses must override destroy_all_operations()!')

    def is_dirty(self) -> bool:
        raise NotImplementedError('subclasses must override is_dirty()!')

    def save_changes(self):
        raise NotImplementedError('subclasses must override save_changes()!')

    def discard_changes(self):
        raise NotImplementedError('subclasses must override discard_changes()!')

    def filter_data(self, data_type, payload):
        raise NotImplementedError('subclasses must override filter_data()!')
