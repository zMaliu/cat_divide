import numpy as np

"归一化向量"
def normalize_vector(vector: list) -> list:
    """归一化向量 - 从server项目提取"""
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return (np.array(vector) / norm).tolist()

"计算余弦相似度"
def cosine_similarity(vec1: list, vec2: list) -> float:
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

"计算欧式距离"
def euclidean_distance(vec1: list, vec2: list) -> float:
    return np.linalg.norm(np.array(vec1) - np.array(vec2))