from PyQt6.QtGui import QUndoCommand

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item, description="Add Item"):
        super().__init__(description)
        self.scene = scene
        self.item = item
        
    def redo(self):
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        
    def undo(self):
        self.scene.removeItem(self.item)

class AddMultipleItemsCommand(QUndoCommand):
    def __init__(self, scene, items, description="Add Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items
        
    def redo(self):
        for item in self.items:
            if item not in self.scene.items():
                self.scene.addItem(item)
        
    def undo(self):
        for item in self.items:
            self.scene.removeItem(item)

class RemoveItemsCommand(QUndoCommand):
    def __init__(self, scene, items, description="Remove Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items
        
    def redo(self):
        for item in self.items:
            self.scene.removeItem(item)
            
    def undo(self):
        for item in self.items:
            if item not in self.scene.items():
                self.scene.addItem(item)
