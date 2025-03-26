from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.providers.aer import QasmSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import random_statevector
import numpy as np

# Function to create a Bell pair between two qubits
def create_bell_pair(qc, a, b):
    qc.h(a)  # Apply Hadamard to create superposition
    qc.cx(a, b)  # Apply CNOT to entangle qubits

# Function for Alice's measurement
def alice_measure(qc, psi, a):
    qc.cx(psi, a)  # CNOT with psi as control
    qc.h(psi)  # Hadamard on psi
    qc.measure(psi, 0)  # Measure psi
    qc.measure(a, 1)  # Measure Alice's entangled qubit

# Function for Bob's correction based on classical bits
def bob_correct(qc, b, c1, c2):
    qc.x(b).c_if(c2, 1)  # Apply X gate if c2 = 1
    qc.z(b).c_if(c1, 1)  # Apply Z gate if c1 = 1

# Main teleportation simulation
def quantum_teleportation(noisy=False):
    # Define registers
    qreg = QuantumRegister(3, 'q')  # 3 qubits: psi (to teleport), Alice's, Bob's
    creg = ClassicalRegister(2, 'c')  # 2 classical bits for measurement
    qc = QuantumCircuit(qreg, creg)

    # Step 1: Prepare an arbitrary state to teleport (random statevector)
    psi = random_statevector(2)
    qc.initialize(psi.data, 0)  # Initialize qubit 0 with random state
    qc.barrier()

    # Step 2: Create Bell pair between Alice (q1) and Bob (q2)
    create_bell_pair(qc, 1, 2)
    qc.barrier()

    # Step 3: Alice's operations
    alice_measure(qc, 0, 1)
    qc.barrier()

    # Step 4: Bob's corrections
    bob_correct(qc, 2, creg[0], creg[1])

    # Simulate the circuit
    if noisy:
        from qiskit.providers.aer.noise import NoiseModel
        from qiskit.providers.aer.noise.errors import depolarizing_error
        noise_model = NoiseModel()
        error = depolarizing_error(0.05, 1)  # 5% depolarizing noise
        noise_model.add_all_qubit_quantum_error(error, ['h', 'cx'])
        backend = QasmSimulator(noise_model=noise_model)
    else:
        backend = Aer.get_backend('qasm_simulator')

    # Run the circuit
    job = execute(qc, backend, shots=1024)
    result = job.result()
    counts = result.get_counts()

    # Visualize results
    print("Original state to teleport:", psi.data)
    print("Measurement counts:", counts)
    return qc, counts

# Run the simulation
circuit, counts = quantum_teleportation(noisy=True)  # Set noisy=True to simulate noise
print(circuit)
plot_histogram(counts).show()

