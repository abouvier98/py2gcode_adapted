# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 13:31:09 2025

@author: antob
"""


"""Functions that can be applied to pg to add command to the gcode file""" 
# first initialisation
def init_first(pg, x0, y0, z0):
    pg.calib_axis()
    pg.cold_print()
    pg.offset_origin(x0 = 23, y0 = 6.5)
    pg.go_home(x = True, y = True, z = True)
    pg.set_zero(extrude = True)
    pg.move_abs(z = 12.0) # rise the nozzle 12.0 [mm] 
    pg.move_abs(x = 0.91)
    pg.move_abs(z = 10.455)
    pg.move_abs(z = 12.0)
    pg.move_abs(x = 18.0 + x0,y = 102.5 - y0) # initial position for printing from top left
    pg.move_abs(z = z0)

# initialisation just for y and x (z keot at the previous value)
def init_after(pg, x0, y0, z0):
    pg.calib_axis()
    pg.cold_print()
    pg.offset_origin(x0 = 23, y0 = 6.5)
    pg.set_zero(extrude = True)
    pg.set_position(z = 10.0)
    pg.go_home(x = True, y = True, z = False)
    pg.move_abs(z = 12.0) # rise the nozzle 12.0 [mm] 
    pg.move_abs(x = 0.91)
    pg.move_abs(z = 10.455)
    pg.move_abs(z = 12.0)
    pg.move_abs(x = 18.0 + x0,y = 102.5 - y0) # initial position for printing from top left
    pg.move_abs(z = z0)

def drop(pg,E = None):
    if E != None:
        pg.extrude_only(E=E)
    else:
        pg.extrude_only(E=0.15)
    
def drop_depose(pg):
    pg.move(z = -2.0)
    pg.pause(time = 2000)
    pg.move(z = 2.0)

# print line with vertical start and end
def line_sharp(pg, l, P, y1 =None, y2 = None, Ve = None):
    pg.move(z = -2.0)
    if y1 != None:
        pg.move(y = y1, feed = 600.0)
    pg.move(y = l, extrude = True, V = Ve)
    if y2 != None:
        pg.move(y = y2, feed = 600.0)
    pg.pause(time = P)
    pg.move(z = 2.0)
    
# print line with inclined start and end
def line_slope(pg, l, y1 = None, y2 = None, y3 = None, y4 = None, Ve = None, feed = None):
    if feed != None:
        f = feed
    else:
        f = 600
    if y1 != None:
        pg.move(y= y1, z = -1.0, feed = f)
    if y2 != None:
        pg.move(y = y2,  z = -1.0, feed = f, extrude = True, V = 10/3)
    pg.move(y = l, extrude = True, V = Ve)
    if y3 != None:
        pg.move(y = y3, feed = f)
    if y4 != None:
        pg.move(y= y4, z = 2.0, feed = 600.0)
    
# print line with inclined start and end in x direction
def line_slope_x(pg, l, x1 = None, x2 = None, x3 = None, x4 = None, Ve = None, feed = None):
    if feed != None:
        f = feed
    else:
        f = 600
    if x1!= None:
        pg.move(x= x1, z = -1.0, feed = f)
    if x2 != None:
        pg.move(x = x2,  z = -1.0, feed = f, extrude = True, V = 10/3)
    pg.move(x = l, extrude = True, V = Ve)
    if x3 != None:
        pg.move(x = x3, feed = f)
    if x4 != None:
        pg.move(x= x4, z = 2.0, feed = 600.0)
        
# print line with inclined start and end in x direction
def line_slope_2D(pg, l, x1 = None, x2 = None, x3 = None, x4 = None, Ve = None, feed = None):
    if feed != None:
        f = feed
    else:
        f = 600
    if x1!= None:
        pg.move(x= x1, z = -1.0, feed = f)
    if x2 != None:
        pg.move(x = x2,  z = -1.0, feed = f, extrude = True, V = 10/3)
    pg.move(x = l, extrude = True, V = Ve)
    if x3 != None:
        pg.move(x = x3, feed = f)
    if x4 != None:
        pg.move(x= x4, z = 2.0, feed = 600.0)
    
