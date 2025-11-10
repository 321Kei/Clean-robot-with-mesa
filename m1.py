import mesa
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import pandas as pd

# Clean robot
class RobotAgent(mesa.Agent):
    """
    An agent, clean robot, cleans dirty cells and move randomly.
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

#Dirty
class Dirt(mesa.Agent):
    """
    Represents a dirty cell
    """
    def __init__(self, model, pos=None):
        super().__init__(model) 
        self.pos = None

# Model 
class RoomModel(mesa.Model):
    """
    Model of a reactive cleaning robot
    """
    def __init__(self, M, N, initial_dirt_perc, max_time, seed=None):
        

        super().__init__(seed=seed)
        
        self.M = M
        self.N = N
        self.num_agents = 2
        self.initial_dirt_perc = initial_dirt_perc
        self.max_time = max_time
        self.running = True
        self.total_cells = M * N
        self.steps_to_clean = -1
        self.agents_list = []
        self.grid = mesa.space.MultiGrid(self.M, self.N, torus=False)
        
    
        for _ in range(self.num_agents):
            a = RobotAgent(self)
            self.agents_list.append(a)
            self.grid.place_agent(a, (1, 1)) 


        self.initial_dirty_count = int(self.total_cells * initial_dirt_perc / 100)
        self.dirty_cells = self.initial_dirty_count
        all_coords = [(x, y) for x in range(self.M) for y in range(self.N)]
        dirty_positions = self.random.sample(all_coords, self.initial_dirty_count)


        for x, y in dirty_positions: 
             dirt = Dirt(self, (x, y))
             self.grid.place_agent(dirt, (x, y))
            

        self.datacollector = DataCollector(
            model_reporters={
                "Time": "steps",
                "Clean_Percentage": lambda m: (m.total_cells - m.dirty_cells) / m.total_cells * 100,
                "Total_Movements": lambda m: sum(a.movements for a in m.agents_list)
            }
        )
        self.datacollector.collect(self)

    def step(self):
        """
        Update
        """
        # All is clean
        if self.steps >= self.max_time:
            self.running = False
            return
        
        if self.dirty_cells == 0:
            if self.steps_to_clean == -1:
                self.steps_to_clean = self.steps
            self.running = False
            return
            
        #It's no clean
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)



if __name__ == "__main__":
    M = 10
    N = 10
    initial_dirt_perc = 70
    max_time = 200
    seed = None
    
    model = RoomModel(
        M=M, 
        N=N, 
        initial_dirt_perc=initial_dirt_perc, 
        max_time=max_time,
        seed=seed
    )
    
    while model.running:
        model.step()
    
    model_data_df = model.datacollector.get_model_vars_dataframe()
    final_data = model_data_df.iloc[-1]

    print(f"Total execution time: {model.steps} steps")
    print(f"Time to clean all cells: {model.steps_to_clean if model.steps_to_clean != -1 else 'Not reached'}")
    print(f"Final percentage of clean cells: {final_data['Clean_Percentage']:.2f}%")
    print(f"Number of movements: {final_data['Total_Movements']:.0f}")
