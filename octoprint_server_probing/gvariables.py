#parse gcode for variables and handle them on the server
class gvariables:

    def __init__(self):
#        self.variables={2002:0.0,100:0.0,648:0.0,649:0.0,650:0.0,651:0.0,652:0.0}
        self.variables={2002:1.1}


    def replace(self, line):
#stop us hitting the end
        line=line+' '
        out=""
        expr=""
        letter=0 
        brackets=0
        evaluate=False
        while letter<len(line):  
#remove gcode comments
            if line[letter]=="(":
                letter+=1 
                if ')' in line[letter:]:
                    end=line[letter:].find(')')
                    letter+=end
#                    while not ')' is line[letter]:
#                        letter+=1 
                else:
                    return out 
#replace variables with value
            elif line[letter]=="#":
                letter+=1
                start=letter
                while line[letter] in '0123456789':
                    letter+=1
                end=letter
                variable=int(line[start:end])
                letter=letter-1
                if not evaluate:
                    out+=str(self.variables[variable])
                else:
                    expr+=str(self.variables[variable])
            elif line[letter]=="[":
                evaluate=True
                expr+="("
                brackets+=1
            elif line[letter]=="]":
                expr+=")"
                brackets+=-1
                if brackets == 0 :
                   evaluate=False
                   value=eval(expr)
                   out+=str(value)
            else:
                if evaluate:
                    expr+=line[letter]
                else:
                    out+=line[letter]
            letter+=1
        return out 

    def evaluate(self,expr):
        value=eval(self.replace(expr))
        return value

#Example gcode lines
# set variable
# #107 = 0
# get  variable
# #501=#2002
# calculation with variables
# #1=[#502+[#503-#502]*0.17541]
# Gcode values calculated from variables
# X2.80157 Y-1.29528 Z[#3+-0.03937]
    def parse(self, line):
#        Remove= (None,)
        Remove= None,
#We control our spindle manually, so best not to confuse the machine by
#telling it to do it
        if line[:3]=='M5 ':
            return Remove 
#also don't send command to set direction
        elif line[:3]=='M3 ':
            return Remove 
#also don't set spindle speed (speed is set to 123456 in the pcb2gcode 
#configuration file to allow this) 
        elif line.find("S123456") != -1 :
            return Remove 
#some lines don't repeat G1. Best fix that to be sure
#is this setting a variable?
        elif line[0]=="#":
            set=int(line[1:line.find("=")])
            terms=line[line.find("=")+1:] 
            replaced=self.replace(terms) 
            new=eval(replaced) 
            self.variables[set]=new
#remove this line
            return Remove 
#do variables need replacing with calculated values?
#some lines don't repeat G1. Best fix that to be sure
        if line[0] in 'XYZ':
            line="G1 "+line
        line=self.replace(line)
        return line

