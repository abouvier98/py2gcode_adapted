# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 14:37:37 2022
@author: alejandro
https://github.com/AlejandroIbarraO/py2gcode/tree/main

Modified & completed on Mon Feb 03 15:41:29 2025
@author : antob

"""
import numpy as np
import matplotlib.pyplot as plt

class py2gcode:
    def __init__(self, material_diameter =12.5,nozzle_diameter = 0.91,esteps = 0):
        self.material_diameter = material_diameter
        self.nozzle_diameter = nozzle_diameter
        self.line_diameter = self.nozzle_diameter
        self.extrude_factor = (self.line_diameter/self.material_diameter)**2
        self.command_history = []
        self.position = {'x' : [0],'y' : [0], 'z': [0], 'E':['tab:blue'], 'L':[0]}
        self.extruded_lenght = 0
        self.output = 'file'  # serial or file.GCODE
        self.esteps = esteps # flow calculated in the printhead 1 or via software 0
        self.pulses_ul = 49
        self.flow_multiplier = 1
        self.layer_thickness = self.line_diameter
        self.layer = 0
        self.current_toolhead = 0
        self.color_head = ['tab:red','tab:green','tab:orange']
        self.relative = True
        self.feed = 600. # mm/min 600 it's 10 mm/s
        self.feednoprint = 1200.
        # retraction parameters
        self.retraction_speed = 5000.0 # steps per seconds 
        self.retraction_lenght = 5000.0 # steps, current configuration about of 4ul
        self.delay_retraction = 100 # ms
        self.clean_position = (10,10)
        self.clean_count = 0
        self.clean_lenght = 100.0
        self.z_hop_height = 5.0
        self.head_offset = [(0,0,0)] # array with the offset for each head, the firts head hava zero offset
    # def set_zero(self, plane = True):
    #     if plane:
    #         self.command_history.append('G92 X0 Y0')
    #     else:
    #         self.command_history.append('G92 X0 Y0 Z0')
            
    # plastic extrusion parameters
    def set_head(self, T = 0):
        self.current_toolhead = T
        self.command_history.append('T'+str(T))
    def set_temp(self,head = None,tem = 200):
        if head == None:
            head = self.current_toolhead
        self.command_history.append('M109 T'+str(head) +' S'+str(tem))
    def set_offset(self, toolhead,offset):
        if toolhead != 0:
            self.command_history.append('M6 '+ 'T'+str(toolhead) + ' X'+str(offset[0])+ ' Y'+str(offset[0])+ ' Z'+str(offset[2]))
    def set_bed_tem(self, tem = 0):
        self.command_history.append('M140 S'+str(tem))
    def layer_h(self, h):
        self.command_history.append('M756 S'+str(h))
    def config_retraction(self):
        if self.esteps == 1:
            self.command_history.append('M722'+ ' S' + str(self.retraction_speed)+
                                          ' E' + str(self.retraction_lenght)+
                                          ' P' + str(self.delay_retraction)+
                                          ' T' + str(self.current_toolhead))
            self.command_history.append('M721'+ ' S' + str(self.retraction_speed)+
                                          ' E' + str(self.retraction_lenght)+
                                          ' P' + str(self.delay_retraction)+
                                          ' T' + str(self.current_toolhead))   
        else:
            self.command_history.append('M207'+ ' F' + str(self.retraction_speed)+
                                          ' S' + str(self.retraction_lenght))   
            self.command_history.append('M208'+ ' F' + str(self.retraction_speed)+
                                          ' S' + str(self.retraction_lenght))
    
    def retract(self):
        if self.relative == False:
            self.command_history.append('G91') # change to relative positioning.
            self.relative = True
        self.command_history.append('G1 E{e:.6} F{f:.6}'.format(e = -float(round(self.retraction_lenght,3)),f =self.retraction_speed))
        self.position['x'].append(self.position['x'][-1])
        self.position['y'].append(self.position['y'][-1])
        self.position['z'].append(self.position['z'][-1])
        self.position['L'].append(self.position['L'][-1]-float(round(self.retraction_lenght,3)))
        self.position['E'].append('tab:gray')
    def recover(self):
        if self.relative == False:
            self.command_history.append('G91') # change to relative positioning.
            self.relative = True
        self.command_history.append('G1 E{e:.6} F{f:.6}'.format(e = float(round(self.retraction_lenght,3)),f =self.retraction_speed))  
        self.position['x'].append(self.position['x'][-1])
        self.position['y'].append(self.position['y'][-1])
        self.position['z'].append(self.position['z'][-1])
        self.position['L'].append(self.position['L'][-1]+float(round(self.retraction_lenght,3)))
        self.position['E'].append('tab:gray')
    def e_config(self,correction = True,flow_mul = None,pulses_ul = None,nozzle_diameter = None):
        if flow_mul == None:
            flow_mul = self.flow_multiplier
        if pulses_ul == None:
            pulses_ul = self.pulses_ul
        if nozzle_diameter == None:
            nozzle_diameter = self.nozzle_diameter
            
        
        # this command configure the extrusion process. Type of extuder control and set the parameters
        if self.esteps == 1:
            ## native calculation of the extruding process
            self.command_history.append('M221'+' P'+str(self.pulses_ul)+
                                        ' S'+str(flow_mul)+
                                        ' Z'+str(self.line_diameter)+
                                        ' W'+str(nozzle_diameter)+
                                        ' T'+str(self.current_toolhead))
            self.command_history.append('M756 S'+str(self.line_diameter))
        else:
            ## local extuding steps calculation
            self.extrude_factor = (self.line_diameter/self.material_diameter)**2
            self.command_history.append('M229 E1 D1 S1')
        if self.relative == True:
            self.command_history.append('G91')
        else:
           self.command_history.append('G90') 
           
    # motion function
    def move(self,x = None,y = None,z = None, extrude = False,feed = None,V = None,extrude_multiplier = 1.0):
        self.extrude_factor = (self.line_diameter/self.material_diameter)**2
        """ this command append a relative move, the flag extrude it is used to 
            set a extrusion move"""
        if self.relative == False:
            self.command_history.append('G91') # change to relative positioning.
            self.relative = True
        if extrude:    
            cmd = 'G1 '
        else:
            cmd = 'G0 '
        if x != None: 
            cmd += 'X{x:.6} '.format(x = float(round(x,3)))
        if y != None: 
            cmd += 'Y{y:.6} '.format(y = float(round(y,3)))
        if z != None: 
            cmd += 'Z{z:.6} '.format(z = float(round(z,3)))
        
        """This define the extrusion rate based on the motion and the extrusion
        factor
        Modification Antoine : add a volume V vairable if we want to impose a volume 
        extruded no matter the distance"""
        if extrude == True:
            if V!= None:
                l = 0.015*V # volume in µL
                cmd += 'E{l:.6} '.format(l = float(round(l,3)))
            else:
                if self.esteps == 1:
                    cmd += 'E1 '
                else:
                    l = 0
                    if x != None: l = l + x**2
                    if y != None: l = l + y**2
                    if z != None: l = l + z**2
    
                    l = np.sqrt(l)*self.extrude_factor*extrude_multiplier
                    #print(l,extrude_multiplier)
                    cmd += 'E{l:.6} '.format(l = float(round(l,3)))
        if extrude:
            if feed == None:
                cmd += 'F{f}'.format(f = self.feed)
            else:
                cmd += 'F{f}'.format(f = feed)
        else:
            if feed == None:
                cmd += 'F{f}'.format(f = self.feednoprint)
            else:
                cmd += 'F{f}'.format(f = feed)
        if x == None: x = self.position['x'][-1]
        else:  x = self.position['x'][-1] +x
        self.position['x'].append(x)
        if y == None: y = self.position['y'][-1] 
        else:  y = self.position['y'][-1] +y
        self.position['y'].append(y)
        if z == None: z = self.position['z'][-1]
        else:  z = self.position['z'][-1] +z
        self.position['z'].append(z)
        if extrude == False: L = self.position['L'][-1]
        else:  L = self.position['L'][-1] +l
        self.position['L'].append(L)
        if extrude == True:
            self.position['E'].append(self.color_head[self.current_toolhead])
        else:
            self.position['E'].append('tab:blue')
        self.command_history.append(cmd)
    def move_abs(self,x = None,y = None,z = None,extrude = False,feed =None,V=None,extrude_multiplier = 1.0):
        self.extrude_factor = (self.line_diameter/self.material_diameter)**2
        if self.relative == True:
            self.command_history.append('G90') # change to absolute positioning.
            self.relative = False
        if extrude:    
            cmd = 'G1 '
        else:
            cmd = 'G0 '
        
        if x != None: 
            cmd += 'X{x:.6} '.format(x = float(round(x,3)))
        if y != None: 
            cmd += 'Y{y:.6} '.format(y = float(round(y,3)))
        if z != None: 
            cmd += 'Z{z:.6} '.format(z = float(round(z,3)))
        
        if extrude == True:
            if V != None:
                l = 0.015*V    # volume in µL
                cmd += 'E{l:.6} '.format(l = float(round(l,3)))
            else:
                l = 0
                if x != None: l = l + (x-self.position['x'][-1])**2
                if y != None: l = l + (y-self.position['y'][-1])**2
                if z != None: l = l + (z-self.position['z'][-1])**2
                l = np.sqrt(l)*self.extrude_factor*extrude_multiplier + self.position['L'][-1]
                if self.esteps == 1:
                    cmd += 'E1 '
                else:
                    cmd += 'E{l:.6} '.format(l = float(round(l,3)))
        if extrude:
            if feed == None:
                cmd += 'F{f}'.format(f = self.feed)
            else:
                cmd += 'F{f}'.format(f = feed)
        else:
            if feed == None:
                cmd += 'F{f}'.format(f = self.feednoprint)
            else:
                cmd += 'F{f}'.format(f = feed)
            
        if x == None: x = self.position['x'][-1]
        self.position['x'].append(x)
        if y == None: y = self.position['y'][-1]
        self.position['y'].append(y)
        if z == None: z = self.position['z'][-1]
        self.position['z'].append(z)
        if extrude == False: l = self.position['L'][-1]
        self.position['L'].append(l)
        if extrude == True:
            self.position['E'].append(self.color_head[self.current_toolhead])
        else:
            self.position['E'].append('tab:blue')
        self.command_history.append(cmd)
    def pos(self,code = 'all'):
        if code == 'all':
            return [self.position['x'][-1],self.position['y'][-1],self.position['z'][-1]]
        if code in ['x','y','z']:
            return self.position[code][-1]
        
    def out(self,name = None):
        if name is None:
            f = open(self.output+'.GCODE','w')
        else:
            f = open(name+'.GCODE','w')
        for command in self.command_history:
            f.write(command+'\n')
        if self.esteps == 1:
            f.write('M30')
        f.close()
    def go_home(self,x = False,y = False,z = False):
        # self.command_history.append('G28 X0 Y0')
        # self.command_history.append('G28 Z0')
        cmd = 'G28 '
        if x: 
            cmd += 'X0 '
        if y: 
            cmd += 'Y0 '
        self.command_history.append(cmd)
        if z: 
            self.command_history.append('G28 Z0')
    def pause(self, time = None):
        if time != None:
            self.command_history.append('G4 P' + str(time)) # pause of time ms
    def calib_axis(self):
        self.command_history.append('M92 T0 E7200 \t ; Define steps/mm') # calibration
    def cold_print(self):
        self.command_history.append('M302 S0 \t ; Allow cold printing')     
    def offset_origin(self, x0 = None, y0 = None, z0 = None):
        cmd = 'M206 '
        if x0 != None: 
            cmd += 'X-{x:.6} '.format(x = float(round(x0,3)))
        if y0 != None: 
            cmd += 'Y-{y:.6} '.format(y = float(round(y0,3)))
        if z0 != None: 
            cmd += 'Z-{z:.6} '.format(z = float(round(z0,3)))
        cmd += '\t ; Add value to endstop positions'
        self.command_history.append(cmd)
    def set_zero(self, plane = False, z = False, extrude = False):
        if plane:
            self.command_history.append('G92 X0 Y0')
        if z:
            self.command_history.append('G92 Z0')
        if extrude: 
            self.command_history.append('G92 E0 \t ; Define position')
    def set_position(self, x = None, y = None, z = None):
        cmd = 'G92 '
        if x != None: 
            cmd += 'X{x:.6} '.format(x = float(round(x,3)))
        if y != None: 
            cmd += 'Y{y:.6} '.format(y = float(round(y,3)))
        if z != None: 
            cmd += 'Z{z:.6} '.format(z = float(round(z,3)))
        cmd += '\t ; Set position'
        self.command_history.append(cmd)        
    def extrude_only(self,E = None):
        cmd = 'G1 '
        if E != None:
            cmd += 'E{E:.6} '.format(E = float(round(E,3)))
            cmd += 'F100.0'
        self.command_history.append(cmd)
            
        
            

    def plot(self, ax = None,fig = None):
        if ax == None and fig == None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
        for i in range(len(self.position['E'])-1):
            ax.plot(self.position['x'][i:i+2],self.position['y'][i:i+2],self.position['z'][i:i+2], c = self.position['E'][i+1])
        return fig,ax

    def clean_nozzle(self, extrude = True):
        self.move(z = self.z_hop_height)
        self.move_abs(x = self.clean_position[0],y = self.clean_position[1]+self.nozzle_diameter*self.clean_count)
        self.move(z = -self.z_hop_height)
        self.move(x = self.clean_lenght, extrude = extrude)
        self.clean_count +=1
    def write(self, command):
        if command != '':
            self.command_history.append(command)
    def material_report(self):
        length = self.position['L'][-1]
        volume = self.position['L'][-1]*0.1*np.pi*(.1*self.material_diameter/2)**2
        return length,volume
def main():
   hy = py2gcode()
   hy.nozzle_diameter = 0.35
   hy.set_head(0)
   hy.e_config()
   hy.feed = 120
   hy.clean_nozzle()
   
   
   hy.out()
   #hy.set_zero()
   return hy
   
if __name__ == '__main__':
    hy = main()
        
            