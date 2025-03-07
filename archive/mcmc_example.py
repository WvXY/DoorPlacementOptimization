import numpy as np


def f(x, normalize=False):
    '''
    Function proportional to target distribution, a sum of Gaussians.
    For testing, set normalize to True, to get target distribution exactly.
    '''
    # Gaussian heights, width parameters, and mean positions respectively:
    a = np.array([10., 3., 1.]).reshape(3, 1)
    b = np.array([ 4., 0.2, 2.]).reshape(3, 1)
    xs = np.array([-4., -1., 5.]).reshape(3, 1)

    if normalize:
        norm = (np.sqrt(np.pi) * (a / np.sqrt(b))).sum()
        a /= norm

    return (a * np.exp(-b * (x - xs)**2)).sum(axis=0)

def g():
    '''Random step vector.'''
    return np.random.uniform(-1,1)

def metropolis_step(x, f=f, g=g):
    '''Perform one full iteration and return new position.'''

    x_proposed = x + g()
    a = min(1, (f(x_proposed) / f(x)).item())

    x_new = np.random.choice([x_proposed, x], p=[a, 1-a])

    return x_new

def metropolis_iterate(x0, num_steps):
    '''Iterate metropolis algorithm for num_steps using iniital position x_0'''

    for n in range(num_steps):
        if n == 0:
            x = x0
        else:
            x = metropolis_step(x)
        yield x


def test_metropolis_iterate(num_steps, xmin, xmax, x0):
    '''
    Calculate error in normalized density histogram of data
    generated by metropolis_iterate() by using
    normalized-root-mean-square-deviation metric.
    '''

    bin_width = 0.25
    bins = np.arange(xmin, xmax + bin_width/2, bin_width)
    centers = np.arange(xmin + bin_width/2, xmax, bin_width)

    true_values = f(centers, normalize=True)
    mean_value = np.mean(true_values - min(true_values))

    x_dat = list(metropolis_iterate(x0, num_steps))
    heights, _ = np.histogram(x_dat, bins=bins, density=True)

    nmsd = np.average((heights - true_values)**2 / mean_value)
    nrmsd = np.sqrt(nmsd)

    return nrmsd



if __name__ == "__main__":
    xmin, xmax = -10, 10
    x0 = np.random.uniform(xmin, xmax)

    num_steps = 50_000

    x_dat = list(metropolis_iterate(x0, 50_000))

    # Write data to file
    output_string = "\n".join(str(x) for x in x_dat)

    with open("output.dat", "w") as out:
        out.write(output_string)
        out.write("\n")


    # Testing
    print(f"Testing with x0 = {x0:5.2f}")
    print(f"{'num_steps':>10s} {'NRMSD':10s}")
    for num_steps in (500, 5_000, 50_000):
        nrmsd = test_metropolis_iterate(num_steps, xmin, xmax, x0)
        print(f"{num_steps:10d} {nrmsd:5.1%}")