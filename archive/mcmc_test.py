import numpy as np
import matplotlib.pyplot as plt


def f(x):
    return -(np.exp(-((x - 1) ** 2)) + 1.5 * np.exp(-((x + 1) ** 2))) + 2


def metropolis_hastings_maximize(f, n_iter=100, T=0.1):
    x = 0  # Initial guess
    best_x = x
    best_f = f(x)
    samples = []

    for i in range(n_iter):
        x_new = x + np.random.normal(0, 0.1)  # Propose a new state
        delta_f = f(x_new) - f(x)
        # print(np.exp(-delta_f / T))

        if delta_f < 0 or np.random.rand() < np.exp(
            -delta_f / T
        ):  # Accept criterion
            x = x_new
            if f(x) > best_f:  # Update the best if necessary
                best_x = x
                best_f = f(x)

        samples.append(x)

    return best_x, best_f, samples


T = 0.1

# Run the algorithm
best_x, best_f, samples = metropolis_hastings_maximize(f, n_iter=200, T=T)

# Display results
print(f"Best x: {best_x}, Best f(x): {best_f}")

# Plot the sampled points
fig, ax1 = plt.subplots()

# Plot histogram on primary y-axis
ax1.hist(samples, bins=40, density=True, alpha=0.8, label="Samples")
ax1.set_ylabel("Density (Histogram)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")

# Create secondary y-axis
ax2 = ax1.twinx()

# Plot f(x) on secondary y-axis
x_vals = np.linspace(-2, 4, 60)
ax2.plot(x_vals, f(x_vals), label="f(x)", color="red")
ax2.set_ylabel("f(x)", color="red")
ax2.tick_params(axis="y", labelcolor="red")

# Combine legends from both axes if needed
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="lower right")

plt.xlabel("x")
plt.title(f"Metropolis-Hastings Sampling for Minimizing f(x) | T={T}")
plt.savefig(f"mcmc_demo_T{T}.svg")
plt.show()
