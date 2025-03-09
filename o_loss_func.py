import numpy as np


def loss_func(path):
    total_cost = 0
    total_cost += traffic_loss_func(path)
    return total_cost


def traffic_loss_func(path):
    return sum(
        np.linalg.norm(path[i].xy - path[i + 1].xy)
        for i in range(len(path) - 1)
    )


def entrance_loss_func(doors, target_dist=0.1):
    """Every door to the entrances"""
    loss = 0
    for d in doors:
        for dd in doors:
            if d == dd:
                continue
            dist = np.linalg.norm(d.xy - dd.xy)

            if dist < target_dist:
                loss += (target_dist - dist) ** 2

    return loss
