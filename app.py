import sys 
from PyQt5.QtWidgets import QApplication    
from views.menu import MainMenu
from model.menu_model import MenuModel
from model.tool_model import ToolModel
from model.year_panel_model import YearPanelModel
from model.widget_models import ClassificationModel, RegistrationModel
from controller.menu_controller import MenuController
from controller.tool_controller import ToolController
from controller.year_panel_controller import YearPanelController
from controller.widget_controllers import ClassificationController, RegistrationController
from views.annotation_tool import AnnotationTool
from views.year_panel import YearPanel
from views.menu_widgets import ClassificationMenu, RegistrationMenu
from database.db import SlabInventory
class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.slab_inventory = SlabInventory()
        self.menu_model = MenuModel(self.slab_inventory)
        self.classification_model = ClassificationModel(
            self.slab_inventory, self.menu_model
            )
        self.classification_controller = ClassificationController(
            self.classification_model, self
            )
        self.classification_view = ClassificationMenu(
            self.classification_controller, self.classification_model
            )
        self.registration_model = RegistrationModel(
            self.slab_inventory, self.menu_model
            )
        self.registration_controller = RegistrationController(
            self.registration_model, self
            )
        self.registration_view = RegistrationMenu(
            self.registration_controller, self.registration_model
            )
        self.menu_controller = MenuController(self.menu_model)
        self.menu = MainMenu(self.menu_controller, self.menu_model, 
                             self.classification_view, self.registration_view)
        self.menu.show()


    def run_registration_script(self):
        pass


    def run_annotation_tool(self):
        """Runs the annotation tool window after the user submits the main menu
        form. The main menu window is closed and the annotation tool window is
        opened.
        """

        reg_data = self.classification_model.registrations[
            self.classification_model.registration
            ]
        dir = self.menu_model.directory
        #self.slab_inventory.set_segment(reg_data['_id'])
        self.year_panels = {}
        self.year_controllers = {}
        self.year_models = {}

        # Each year to annotate has its own MVC components
        for year in reg_data['years']:
            year_model = YearPanelModel(year, self.slab_inventory, reg_data['segment_id'])
            year_controller = YearPanelController(year_model)
            year_view = YearPanel(year_controller, year_model)
            self.year_models[year] = year_model
            self.year_controllers[year] = year_controller
            self.year_panels[year] = year_view

        # set up the clasification widgets
    
        self.tool_model = ToolModel(self.year_models, self.slab_inventory, 
                                    dir, reg_data)
        self.tool_controller = ToolController(self.tool_model,
                                              self.year_controllers)  
        self.annotation_tool = AnnotationTool(self.tool_controller, 
                                              self.tool_model, 
                                              self.year_panels)
        self.annotation_tool.show()


if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())    