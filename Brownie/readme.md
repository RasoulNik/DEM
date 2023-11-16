
<span style="color:blue">

## Disclaimer

This project is a research endeavor and has not been tested for real-world deployment. It is important to note that the security aspects of the smart contracts involved in this project have not been fully explored or tested. This is because the focus of this work is not on security testing but rather on the conceptual demonstration and research aspects of decentralized marketplaces. Users should be aware that deploying these contracts in a live environment without proper security validation may pose risks. As always with blockchain and smart contract development, thorough testing and security audits are recommended before any real-world implementation.

</span>

# Decentralized Energy Marketplace (DEM) using Brownie

## Deployment Guide for DEM using Brownie

This guide walks you through setting up and running a demo of the decentralized energy marketplace (DEM) using Brownie, a Python-based development and testing framework for smart contracts.

### Prerequisites
Before proceeding, ensure you have the following installed:
1. **Node.js and npm**: Required for Ganache. [Download Node.js and npm](https://nodejs.org/en/download/).
2. **Ganache**: A personal blockchain for Ethereum development. Install it using npm:
   ```bash
   npm install -g ganache-cli
   ```
   Alternatively, you can use the [Ganache GUI application](https://www.trufflesuite.com/ganache).

### Setting Up the Project
1. **Clone the Repository**: Clone the GitHub repository containing the Brownie project.
2. **Install Dependencies**: Navigate to the project directory and install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Add Required Packages**: Install the Chainlink and OpenZeppelin packages via Brownie:
   ```bash
   brownie pm install smartcontractkit/chainlink-brownie-contracts@1.1.1
   brownie pm install OpenZeppelin/openzeppelin-contracts@4.4.0
   ```

### Running the DEM Simulation
1. **Start Ganache**: Launch Ganache, either using the CLI or the GUI application. Ensure it's running on the same network configuration as specified in your Brownie project.
2. **Compile the Contracts**: Compile the smart contracts in your Brownie project:
   ```bash
   brownie compile
   ```
3. **Run the DEM Simulation**: Navigate to the `tests` folder and execute the `DEM.py` script:
   ```bash
   brownie run DEM.py
   ```
   This script simulates the decentralized energy market scenario, including:
   - Deploying the `EnergyProfile`, `EnergyPool`, and `EnergyMarket` contracts.
   - Registering users and creating energy commitments.
   - Processing and settling these commitments in the market.

### Understanding DEM.py
The `DEM.py` script is the core of the simulation, involving several key steps:
- **Connecting to the Ganache Network**: It connects to your local Ganache blockchain.
- **Deploying Contracts**: It deploys the necessary contracts to the blockchain.
- **Simulating Market Interactions**: The script registers users, creates commitments, and simulates interactions within the energy market.
- **Settling Commitments**: It demonstrates how commitments are settled between users in the marketplace.

### GUI for Interaction (Optional)
For a more interactive experience, a GUI is provided to deploy contracts, settle commitments, compute gas usage, and plot gas usage. This can be accessed through:
- **Gradio Interface**: Use the provided interfaces for deploying, settling, and other operations.
- **Tkinter GUI**: A simple Python GUI for deployment and interaction (if code provided).

---

Make sure to customize this guide according to the specific details and requirements of your project. This template provides a general outline based on the information you provided.

## How DEM Works
The decentralized energy marketplace (DEM) operates on a smart contract ecosystem, encompassing the `EnergyProfile`, `EnergyPool`, and Oracle contracts for price, energy produced, and energy consumed. This system is built to facilitate efficient and transparent energy trading within a blockchain framework.

### Commitment Processing and Buffer Management
The `EnergyMarket` contract plays a pivotal role in managing energy commitments through its `market_buffer`. This buffer is an array of structs, each containing a Profile NFT ID and a commitment detail. The primary function, `process_buffer()`, is tasked with processing these commitments. It starts by invoking `check_expired_commitments()` to purge any outdated commitments, ensuring the buffer remains current. The process then iterates over the buffer, focusing on commitments marked as processed by the `EnergyPool`. If the energy produced is less than the committed consumption for the current interval, the `processCommitment()` function is triggered, which updates the energy produced and consumed, calculates the cost or revenue based on the current price, and sets the commitment's `energy_market_processed` status to true.

### Interval Management and Settlement
The `EnergyMarket` smart contract also handles interval management, crucial for balancing supply and demand in real-time. The current interval is actively monitored and updated, with energy production and consumption data fed by Oracles. The `settle_commitment()` function plays a key role in finalizing transactions between energy producers and consumers. It leverages Oracles to verify the status of each commitment, settling payments based on market prices and available collateral. This function ensures that commitments are accurately settled, marking them as 'settled' in the system, thereby completing the transaction cycle within the decentralized energy market.

### Oracle Integration and Market Dynamics
Oracles are integral to the DEM, providing real-time data on energy prices, production, and consumption. This information is vital for the `processCommitment()` and `settle_commitment()` functions to accurately compute costs, revenues, and settle transactions. The dynamic interaction between these Oracles and the smart contracts allows the DEM to adapt to real-world energy market conditions, ensuring a fair, transparent, and efficient energy trading platform.

In summary, the DEM leverages a sophisticated combination of smart contracts and real-time data inputs to facilitate a robust and dynamic energy trading environment. This system ensures transparency, efficiency, and fairness in energy trading, harnessing the power of blockchain technology to revolutionize the energy market.





## Description of Contracts

### EnergyProfile.sol

#### General Characteristics and Functionality:
- Implements an ERC721 token, representing user energy profiles in the decentralized energy market.
- Manages user data, including energy production, consumption, and commitments.
- Incorporates price oracles for dynamic pricing.

#### Interaction with Other Contracts:
- Interacts with `EnergyPool` and `EnergyMarket` contracts for commitment management and market participation.
- Utilizes Chainlink oracles (`AggregatorV2V3Interface`) for real-time energy data and pricing.

#### Role in the Decentralized Energy Marketplace:
- Central to user participation, representing their stake in the market.
- Facilitates energy trading by tracking production, consumption, and commitments.
- Influences market dynamics through real-time data integration from oracles.

### EnergyPool.sol

#### General Characteristics and Functionality:
- Manages the pooling of energy commitments from multiple users.
- Tracks and updates energy commitments and intervals for production and consumption.
- Supports deposit and withdrawal functionalities for ERC721 tokens.

#### Interaction with Other Contracts:
- Heavily reliant on `EnergyProfile` for user data and commitment details.
- Communicates with `EnergyMarket` for processing and settling commitments.

#### Role in the Decentralized Energy Marketplace:
- Acts as a collective platform for users to pool their energy resources.
- Balances energy supply and demand across different time intervals.
- Enables efficient management of energy resources in the market.

### EnergyMarket.sol

#### General Characteristics and Functionality:
- Facilitates the trading of energy commitments between producers and consumers.
- Manages a buffer of commitments to be processed and settled in the market.
- Integrates with price oracles for market pricing.

#### Interaction with Other Contracts:
- Interacts closely with `EnergyProfile` for commitment details and `EnergyPool` for energy balancing.
- Processes and settles commitments based on market dynamics and user commitments.

#### Role in the Decentralized Energy Marketplace:
- Central to the operation of the energy trading market.
- Ensures fair and efficient matching of energy supply and demand.
- Influences pricing and settlement of energy trades.

This documentation provides a high-level overview of each contract, focusing on their core functionalities, interactions, and roles within the decentralized energy marketplace. For further details, specific function descriptions and technical specifications would be included in a comprehensive technical documentation.