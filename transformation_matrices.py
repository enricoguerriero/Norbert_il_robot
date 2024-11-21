import numpy as np

def transformation_with_transformation_matrix(transformation_matrix, vector):
    
    transformation_matrix = np.array(transformation_matrix)
    vector = np.append(np.array(vector), 0)
    print(transformation_matrix)
    print(vector)
    
    if transformation_matrix.shape != (3, 3):
        print("Transformation matrix must be 3x3")
        return None
    if vector.shape != (3,):
        print("Vector must be 3x1")
        return None
    
    real_world_position_vector = np.dot(transformation_matrix, vector)
    real_world_position_vector = tuple(real_world_position_vector[:-1])
    print(real_world_position_vector)
    
    return real_world_position_vector