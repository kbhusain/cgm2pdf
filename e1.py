

import os, sys

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm as CM 
from reportlab.lib.units import inch as INCHES 

print "CM = ", CM 
print "IN = ", INCHES 
c = canvas.Canvas("B.pdf") 
c.drawString(2*CM ,4*CM,"LID") 
c.drawString(4*CM ,4*CM,"Kamran") 
c.drawString(4*CM ,2*CM,"Husain") 
c.showPage() 
c.save() 
