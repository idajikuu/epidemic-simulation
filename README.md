## Epidemic Simulation: A Probabilistic Model

This project presents a Python-based simulation designed to model the spread of an epidemic using fundamental probabilistic principles. By adjusting key parameters, the simulation captures dynamic behaviors within a population, offering insights into how epidemics evolve under different conditions.

### Core Model Parameters:
- **Infection Radius (r):** Defines the spatial range within which agents can transmit the infection.
- **Transmission Probability (p):** Represents the likelihood of infection upon contact, where \( 0 \leq p \leq 1 \).
- **Infection Duration (\(T\)):** The time period during which an infected agent remains contagious.
- **Mortality Rate (m):** The probability that an infected agent succumbs to the disease, \( 0 \leq m \leq 1 \).
- **Quarantine Response Time (\(Q\)):** Time delay before infected agents are isolated.

The system evolves by iteratively applying these parameters, simulating real-world epidemic dynamics, such as rapid spread, self-limitation due to mortality, and the impact of quarantine measures.

### Highlights:
- **Stochastic Interactions**: The simulation leverages random processes to mimic the unpredictable nature of disease transmission.
- **Realistic Dynamics**: Observe how diseases with high \(p\) and low \(m\) mirror persistent outbreaks, while those with high \(m\) self-limit.
- **Visual Insights**: 3D visualizations powered by OpenGL bring the simulation to life, showcasing agents’ states and movements in real-time.


![utils_frame (2)](https://github.com/user-attachments/assets/c33501ed-5c00-4ce2-98f7-b6aa2f819db1)
[Demonstration](https://www.dropbox.com/scl/fi/hrmki1hugs49tzvydcv1b/Untitled-video-Made-with-Clipchamp_1731358279388.mp4?rlkey=itfvkkgo020hw25dpu3bp07zu&st=uohmsace&raw=1)
