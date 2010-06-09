# -*- coding: utf-8 -*-
import random,cells
import math
class AgentMind:
  def __init__(self, args):
    if not args:
        self.type = 0 # first agent, stand on plant, scan map for plants and 
    elif args[0] == 1:
        self.type = 1
        self.destination = args[1]
    else:
        self.type = args[0]
    
    self.plants = []
    self.sent = []
    self.plant = None
    self.scan = 0
    
    self.my_plant = None
    
    self.target_range = 51
    
    self.tx = random.randrange(-3,4)
    self.ty = random.randrange(-3,4)
    
    self.emergency = 0
    self.ex = 0
    self.ey = 0
    
    # reproduce until you have enough children
    self.children = 0
    
    self.explorer = 0
    
    pass
  
  def dist(self, (x1, y1), (x2, y2)):
      return abs(x1 - x2) + abs(y1 - y2)
  
  def act(self,view,msg):
    x_sum = 0
    y_sum = 0
    dir = 1
    n = len(view.get_plants())
    me = view.get_me()
    mp = (mx,my)= me.get_pos()
    
    # Eat if my energy is low
    if (((me.energy < 51) and (view.get_energy().get(mx, my) > 0))) :
        return cells.Action(cells.ACT_EAT)
    
    if self.type == 0:
        if self.scan:
            energy = view.get_energy()
            for y in range(299):
                for x in range(299):
                    if energy.get(x,y) > 10:
                        self.plants.append((x+1,y))
            self.scan = 0
        
        if not self.plant:
            self.plant = view.get_plants()[0]
            self.scan = 1
            return cells.Action(cells.ACT_MOVE, self.plant.get_pos())
            
        if self.plants != []:
            for (x,y) in self.plants:
                self.plants.remove((x,y))
                if self.dist((x,y), self.plant.get_pos()) < 5:
                    continue
                done = 0
                for dest in self.sent:
                    if self.dist(dest, (x,y)) < 5:
                        done = 1
                        break
                if done:
                    continue
                
                self.sent.append((x,y))
                return cells.Action(cells.ACT_SPAWN, (x,y,1,(x,y)))
        else:
            self.type = 2
    elif self.type == 1:
        (x,y) = self.destination
        dx = x - mx
        dy = y - my
        if dx == 0 and dy == 0:
            self.type = 2
        
        """if abs(dx) > 0:
            dx = math.copysign(1, dx)
        if abs(dy) > 0:
            dy = math.copysign(1, dy)
        return cells.Action(cells.ACT_MOVE, (mx + dx + random.randrange(-1,2), my + dy + random.randrange(-1,2)))"""
        return cells.Action(cells.ACT_MOVE, (x,y))
    
    if self.type != 2:
        return cells.Action(cells.ACT_MOVE,(mx,my))

    # check for walls
    if(mx == 0 or mx == 299):
        self.tx *= -1
    if(my == 0 or my == 299):
        self.ty *= -1

    #If I see an enemy, call for help and attack
    for a in view.get_agents():
        if (a.get_team()!=me.get_team()):
            msg.send_message((1, mx,my))
            return cells.Action(cells.ACT_ATTACK,a.get_pos())

    if(n>0):
        if (not self.my_plant or self.explorer):
            # If I find a plant, set it as my home plant if I don't already have one.
            self.my_plant = view.get_plants()[0]
            if (self.my_plant):
                #Try to become the spawning cell
                self.explorer = 0
                self.children = 0
                return cells.Action(cells.ACT_MOVE,self.my_plant.get_pos())
        elif self.my_plant.get_eff()<view.get_plants()[0].get_eff():
            self.my_plant = view.get_plants()[0]
    
    # Eat if my energy is low
    if (((me.energy < self.target_range) and (view.get_energy().get(mx, my) > 0))) :
        return cells.Action(cells.ACT_EAT)
    
    if (self.my_plant and not self.explorer):
        # Fort bulider code
        dist = max(abs(self.my_plant.get_pos()[0] - mx), abs(self.my_plant.get_pos()[1] - my))
        if(dist > 10):
            self.my_plant = None
        else:
            if (self.children > 50):
                self.explorer = 1
            if (not view.get_me().loaded) and ((dist!=6)) and (random.random()>0.5):
                return cells.Action(cells.ACT_LIFT)
            if (view.get_me().loaded) and ((dist==6)):
                return cells.Action(cells.ACT_DROP)
            #if view.get_me().energy < dist*1.5:
            #    (mx,my) = self.my_plant.get_pos()
            #    return cells.Action(cells.ACT_MOVE,(mx+random.randrange(-1,2),my+random.randrange(-1,2)))
            if (mp == self.my_plant.get_pos()):
                return cells.Action(cells.ACT_SPAWN,(mx+random.randrange(-1,2),my+random.randrange(-1,2), 2))
                self.children += 1
            else:
                if (dist == 5 and random.random() < 0.5):
                    # Spawn cells on the fort walls
                    dx = -math.copysign(1,self.my_plant.get_pos()[0]-mx);
                    dy = -math.copysign(1,self.my_plant.get_pos()[1]-my);
                    return cells.Action(cells.ACT_SPAWN,(mx+dx,my+dy, 2))
                    self.children += 1
                else:
                    return cells.Action(cells.ACT_MOVE,(mx + random.randrange(-1,2),my + random.randrange(-1,2)))
    
    # Reproduce!
    if (me.energy > 50 and self.children < 10 and random.random() < 0.5):
        self.children += 1
        return cells.Action(cells.ACT_SPAWN,(mx+random.randrange(-1,2),my+random.randrange(-1,2), 2))
    
    
    if(self.emergency and mx == self.ex and my == self.ey):
        # If I arrive on the place of the accident, stop going there
        self.emergency = 0
    
    
    best = abs(mx-self.ex)+abs(my-self.ey)
    if(not self.emergency):
        best = 2000
    ax = -1
    ay = 0
    for m in msg.get_messages():
        (type, ox,oy) = m
        if (type == 1) :
            dist = abs(mx-ax)+abs(my-ay)
            if dist < best:
                ax = ox
                ay = oy
                best = dist
    if(ax != -1):
        # Set accident spot/state
        self.emergency = 1
        self.ex = ax + random.randrange(-10,11)
        self.ey = ay + random.randrange(-10,11)
    
    
    if(self.emergency and not self.explorer):
        # Go to place of accident
        dx = self.ex - mx
        dy = self.ey - my
        return cells.Action(cells.ACT_MOVE,(mx + dx + random.randrange(-1,2), my + dy + random.randrange(-1,2)))
    
    # Randomly move in starting direction
    return cells.Action(cells.ACT_MOVE,(mx+self.tx+random.randrange(-1,2),my+self.ty+random.randrange(-1,2)))
    return cells.Action(cells.ACT_MOVE,(mx,my))
