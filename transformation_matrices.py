import numpy as np

def transformation_with_transformation_matrix(transformation_matrix, vector):
    
    transformation_matrix = np.array(transformation_matrix)
    vector = np.array(vector)
    
    if transformation_matrix.shape != (3, 3):
        print("Transformation matrix must be 3x3")
        return None
    if vector.shape != (3,):
        print("Vector must be 3x1")
        return None
    
    real_world_position_vector = np.dot(transformation_matrix, vector)
    
    return real_world_position_vector