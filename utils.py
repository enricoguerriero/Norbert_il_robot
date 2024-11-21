def ask_for_a_puck(map_dic):
    '''
    Asks user for a puck to take.
    '''
    puck_to_take = input("Puck to take: ")
    if puck_to_take in map_dic:
        return puck_to_take
    else:
        print("Puck not found.")
        print("Available pucks: ", list(map_dic.keys()))
        print("Choose a puck from the list; if you choose again an invalid one, you will go back to the menu.")
        puck_to_take = input("Puck to take: ")
        if puck_to_take in map_dic:
            return puck_to_take
        else:
            print("Puck not found.")
            return None
        
        
def ask_for_a_place(map_dic, puck_to_move):
    '''
    Asks user for a place to put the puck.
    '''
    print("Where do you want to place the puck?")
    dx = float(input("dx: "))
    dy = float(input("dy: "))
    
    filtered_dic = {key: value for key, value in map_dic.items() if key != puck_to_move}
    if any([dx - map_dic[puck][0] < 1 and dy - map_dic[puck][1] < 1 for puck in filtered_dic]):
        print("You are placing the puck over another puck.")
        # find which is the puck down the one we are placing
        pucks_down = [puck for puck in filtered_dic if dx - filtered_dic[puck][0] < 1 and dy - filtered_dic[puck][1] < 1]
        n_pucks_down = len(pucks_down)
        return (dx, dy, 0 + 30 * n_pucks_down)
    
    if any([dx - filtered_dic[puck][0] < 20 and dy - filtered_dic[puck][1] < 20 for puck in filtered_dic]):
        while any([dx - filtered_dic[puck][0] < 20 and dy - filtered_dic[puck][1] < 20 for puck in filtered_dic]):
            print("You are placing the puck too close to another puck.")
            dx = input("dx: ")
            dy = input("dy: ")
            if any([dx - filtered_dic[puck][0] < 1 and dy - filtered_dic[puck][1] < 1 for puck in filtered_dic]):
                print("You are placing the puck over another puck.")
                pucks_down = [puck for puck in filtered_dic if dx - filtered_dic[puck][0] < 1 and dy - filtered_dic[puck][1] < 1]
                n_pucks_down = len(pucks_down)
                
                return (dx, dy, 0 + 30 * n_pucks_down)
        return (dx, dy, 0)
    
    return (dx, dy, 0)


def is_the_spot_free(map_dic, dx, dy):
    '''
    Checks if the spot is free.
    '''
    return not any([dx - map_dic[puck][0] < 1 and dy - map_dic[puck][1] < 1 for puck in map_dic])