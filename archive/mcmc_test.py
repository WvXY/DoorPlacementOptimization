import numpy as np
import matplotlib.pyplot as plt

def f(x):
    return -(np.exp(-(x - 1) ** 2) + 1.5 * np.exp(-(x + 1) ** 2)) +2

def metropolis_hastings_maximize(f, n_iter=100, T=.1):
    x = 0  # Initial guess
    best_x = x
    best_f = f(x)
    samples = []

    for i in range(n_iter):
        x_new = x + np.random.normal(0, 0.1)  # Propose a new state
        delta_f = f(x_new) - f(x)
        # print(np.exp(-delta_f / T))

        if delta_f < 0 or np.random.rand() < np.exp(-delta_f / T):  # Accept criterion
            x = x_new
            if f(x) > best_f:  # Update the best if necessary
                best_x = x
                best_f = f(x)

        samples.append(x)

    return best_x, best_f, samples

# Run the algorithm
best_x, best_f, samples = metropolis_hastings_maximize(f, n_iter=400)

# Display results
print(f"Best x: {best_x}, Best f(x): {best_f}")

# Plot the sampled points
plt.hist(samples, bins=100, density=True, alpha=0.5, label="Samples")
x_vals = np.linspace(-2, 4, 100)
plt.plot(x_vals, f(x_vals) , label="f(x)", color='red')
plt.legend()
plt.show()
