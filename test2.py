
from matplotlib import image 
from matplotlib import pyplot as plt 

x_values = [1, 2, 3, 4, 5, 6, 7, 8]
y_values = [1, 2, 3, 4, 5, 6, 7, 8]

# Plot the points
plt.scatter(x_values, y_values, marker='o', color='b')

# Customize the plot if needed
plt.title('Scatter Plot of Points')
# plt.imshow(img) 
plt.show() 