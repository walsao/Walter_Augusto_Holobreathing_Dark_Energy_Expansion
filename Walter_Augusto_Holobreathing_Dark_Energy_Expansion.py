import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Physical constants (in natural units: hbar = c = 1)
G = 6.67430e-11 / (1.22e19)**3 * (3.0857e22)**3 / (1.602e-19)**2  # Gravitational constant (eV^-2)
rho_lambda = 1e-9  # Observed dark energy density (eV^4)
H0 = 70 / 3.0857e19 * 3.154e7  # Hubble constant (eV, ~2.3e-18 eV)

# Simulation parameters
Nx, Ny = 100, 100  # 2D grid size
dx = 1.0  # Spatial step (arbitrary units, scaled later)
dt = 1e-2  # Time step (scaled to ~10^8 years)
Nt = 2000  # Number of timesteps
epsilon = 0.01  # Nonlinearity strength
gamma = 0.05  # Damping to stabilize w
Lambda = (rho_lambda)**0.25  # Energy scale to match rho_lambda (eV)

# Initialize breathing field
phi = 0.001 * np.random.randn(Nx, Ny)  # Small perturbations
phi_dot = np.zeros((Nx, Ny))  # Zero initial velocity

# Initialize scale factor (a=1 at t=0)
a = 1.0
a_dot = H0  # Initial expansion rate
a_list, w_list, rho_list = [], [], []

# Breathing potential and derivative
def V(phi):
    return 1 - np.cos(phi) + (epsilon/4) * phi**4

def dV(phi):
    return np.sin(phi) + epsilon * phi**3

# 2D Laplacian
def laplacian(phi):
    return (np.roll(phi, 1, axis=0) + np.roll(phi, -1, axis=0) +
            np.roll(phi, 1, axis=1) + np.roll(phi, -1, axis=1) - 4 * phi) / dx**2

# Set up plots
fig = plt.figure(figsize=(15, 5))
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)

# Initial plot for field
im = ax1.imshow(phi, cmap='viridis', vmin=-0.1, vmax=0.1)
plt.colorbar(im, ax=ax1)
ax1.set_title('Breathing Field \(\phi(x, y, t)\)')
ax1.set_xlabel('x')
ax1.set_ylabel('y')

# Initial plots for a(t) and w(t)
line1, = ax2.plot([], [], label='Scale Factor a(t)')
ax2.set_xlim(0, Nt)
ax2.set_ylim(0, 3)
ax2.set_xlabel('Time Steps (~10^8 years)')
ax2.set_ylabel('a(t)')
ax2.set_title('Cosmic Expansion')
ax2.grid()

line2, = ax3.plot([], [], label='w(t)')
ax3.axhline(y=-1, color='r', linestyle='--', label='w = -1')
ax3.set_xlim(0, Nt)
ax3.set_ylim(-1.5, -0.5)
ax3.set_xlabel('Time Steps (~10^8 years)')
ax3.set_ylabel('w = p / ρ')
ax3.set_title('Equation of State')
ax3.legend()
ax3.grid()

# Evolution loop
frames_to_save = []
for t in range(Nt):
    # Evolve breathing field
    laplacian_phi = laplacian(phi)
    phi_ddot = laplacian_phi - dV(phi) - gamma * phi_dot
    phi_dot += phi_ddot * dt
    phi += phi_dot * dt

    # Calculate energy density and pressure
    kinetic = 0.5 * phi_dot**2
    gradient = 0.5 * ((np.roll(phi, -1, axis=0) - phi)/dx)**2 + 0.5 * ((np.roll(phi, -1, axis=1) - phi)/dx)**2
    potential = V(phi)
    rho = np.mean(kinetic + gradient + potential) * Lambda**4  # Scale to eV^4
    p = np.mean(kinetic - (1/3) * gradient - potential) * Lambda**4
    w = p / rho if rho != 0 else 0

    # Evolve scale factor (Friedmann equations)
    H = np.sqrt(8 * np.pi * G / 3 * rho)  # H = \dot{a}/a
    a_ddot = -4 * np.pi * G / 3 * (rho + 3 * p) * a  # \ddot{a}/a
    a_dot += a_ddot * dt
    a += a_dot * dt

    # Store for plotting
    a_list.append(a)
    w_list.append(w)
    rho_list.append(rho)

    # Save every 10th frame
    if t % 10 == 0:
        frames_to_save.append(t)

# Update function for animation (only for saved frames)
def update(frame_idx):
    t = frames_to_save[frame_idx]
    im.set_array(phi)  # Update field (same at this timestep)
    line1.set_data(range(t + 1), a_list[:t + 1])
    line2.set_data(range(t + 1), w_list[:t + 1])
    return im, line1, line2

# Run animation with fewer frames
ani = animation.FuncAnimation(fig, update, frames=len(frames_to_save), interval=50, blit=True)
ani.save('Walter_Augusto_Holobreathing_Dark_Energy_Expansion.gif', writer='pillow')

# Final printout
print(f"Mean energy density (last 100 steps): {np.mean(rho_list[-100:]):.2e} eV^4 (Target: 1.00e-9 eV^4)")
print(f"Mean w (last 100 steps): {np.mean(w_list[-100:]):.3f}")
plt.show()
