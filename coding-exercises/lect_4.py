#%%
import numpy as np
import matplotlib.pyplot as plt
#%%
x_1 = np.random.randn(10000)
x_2 = np.random.randn(10000)
# %%
x = np.sqrt(x_1**2 + x_2**2)
ray = x*np.exp(-(x**2)/2)
# %%
pdf = plt.hist(x, bins=40, density=True)
plt.ylabel('Probability Density', fontsize=14)
plt.scatter(x, ray, color = "black")
plt.title('PDF for Sum of Gaussian', fontsize=16)
plt.tight_layout()
plt.show()
# %%
