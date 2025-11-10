import mesa

# Clean robot
class RobotAgent(mesa.Agent):
    """
    Un agente (robot) que limpia las celdas sucias y se mueve aleatoriamente.
    """
    
    def __init__(self, model):

        super().__init__(model)
        self.movements = 0
        
    def step(self):
        """
        Every step logic
        """

        # Check if the cell is dirty,
        
        cell_state = self.model.grid.get_cell_list_contents([self.pos])
        
        for item in cell_state:
            if isinstance(item, Dirt):

                self.model.grid.remove_agent(item)
                item.remove() 
                self.model.dirty_cells -= 1
                break
                
        # If the cell is clear, the agent chooses a random direction to move.
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
            self.movements += 1


class Dirt(mesa.Agent):
    """
    Represents a dirty cell
    """
    def __init__(self, model, pos):
        super().__init__(model)
        self.pos = pos