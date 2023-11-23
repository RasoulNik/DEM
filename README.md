# Decentralized Energy Marketplace (DEM) via NFTs and AI-based Agents

## Overview
This project introduces an advanced Decentralized Energy Marketplace (DEM) integrating blockchain technology and artificial intelligence to manage energy exchanges among smart homes with energy storage systems. Using Non-Fungible Tokens (NFTs) to represent unique energy profiles, the system fosters a transparent and secure trading environment. The core innovation lies in leveraging Federated Deep Reinforcement Learning (FDRL) for collaborative and adaptive energy management strategies while maintaining user privacy.

## Key Features
- **Blockchain Integration:** NFTs for individual energy profiles on a smart contract-based marketplace.
- **AI in Energy Systems:** Federated Deep Reinforcement Learning (FDRL) for collaborative energy management.
- **Virtual Power Plants (VPP):** Combining AI agents with household batteries.
- **Oracle Integration:** Utilizing Chainlink for real-time data integration with smart contracts.

## System Model
- **Smart Homes with Energy Storage:** Equipped with AI for energy use monitoring and management.
- **DEM Platform:** A decentralized application (DApp) for secure and transparent energy exchange.
- **FDRL Framework:** Enables smart buildings to refine energy strategies collaboratively.
- **VPP and Grid Operators:** Integration of DEM, smart homes, and FDRL agents to create a VPP.

<div align="center">
  <img src="/webpage/Figs/Framework_Grid.png" alt="System Model" width="600">
</div>

## Blockchain-enabled Smart Contracts
- **EnergyProfile Contract:** Manages participants' energy profiles.
- **EnergyPool Contract:** Handles energy commitments and aggregates supply-demand.
- **EnergyMarket Contract:** Core operational link among contracts, managing transactions and settlements.

<div align="center">
  <img src="/webpage/Figs/Smart-Grid-Blockchain(2).png" alt="Smart Contracts Interaction" width="600">
</div>

## AI-based Agents
- **FDRL Framework:** Combines FL and DRL for decentralized energy management.
- **Local Training Algorithm:** Utilizes SAC technique for model training.

## Performance Evaluation
- **Deployment and Testing:** Using Brownie and Ganache with Chainlink mock contracts.
- **Training of AI Agents:** Dataset analysis and model training results.

<div align="center">
  <img src="/webpage/Figs/gas_usage_bar_plot.png" alt="Gas Usage" width="600">
</div>

<div align="center">
  <img src="/webpage/Figs/Reward-fed_nonfed.png" alt="AI Agents Training" width="600">
</div>

## Future Work
Integration of off-chain AI agent execution using the Zero-Knowledge Machine Learning (ZK-ML) stack to fortify security and reduce blockchain computational demands.
## How to Cite
If you find this work useful for your research, please consider citing:
insert bibtex here

link to arxiv: https://arxiv.org/abs/2311.10406

@misc{nikbakht2023decentralized,
title={Decentralized Energy Marketplace via NFTs and AI-based Agents},
author={Rasoul Nikbakht and Farhana Javed and Farhad Rezazadeh and Nikolaos Bartzoudis and Josep Mangues-Bafalluy},
year={2023},
eprint={2311.10406},
archivePrefix={arXiv},
primaryClass={cs.NI}
}


## Contributions
This work is a collaborative effort of researchers at the Centre Tecnològic Telecomunicacions Catalunya (CTTC/CERCA).

## License
This project is open-source and available under [LICENSE](/LICENSE).

## Acknowledgments
Supported by the Spanish Government (MICCIN & NextGenEU program), ECSEL Joint Undertaking (JU), and the Catalan government. Additional funding from Generalitat de Catalunya and MCIN/AEI.
