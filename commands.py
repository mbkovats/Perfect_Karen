import random

def handle_commands(comm):
    lower = comm.lower()
    
    if lower == "coin":
        if random.randint(0,100)/100 >= 0.50:
            return "`Heads`" 
        return "`Tails`"
        