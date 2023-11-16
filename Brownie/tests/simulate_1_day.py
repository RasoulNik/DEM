import matplotlib.pyplot as plt
import numpy as np
import time
# tests/test_energy_pool.py
import pytest
import pdb
import random
import matplotlib.pyplot as plt
from brownie import (
    EnergyProfile,
    EnergyPool,
    EnergyMarket,
    MockV3AggregatorEnergyProduced,
    MockV3AggregatorEnergyConsumed,
    MockV3AggregatorPrice,
    accounts,
    network,
    chain,
)
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

@pytest.fixture(scope="module")
def setup():
    deployer = accounts[0]

    energy_produced_oracle = MockV3AggregatorEnergyProduced.deploy(18, 1000000000, {"from": deployer})
    energy_consumed_oracle = MockV3AggregatorEnergyConsumed.deploy(18, 900000000, {"from": deployer})
    energy_price_oracle = MockV3AggregatorPrice.deploy(18, 2000, {"from": deployer})

    energy_profile = EnergyProfile.deploy(
        energy_produced_oracle.address,
        energy_consumed_oracle.address,
        energy_price_oracle.address,
        {"from": deployer},
    )

    energy_market = EnergyMarket.deploy({"from": deployer})

    energy_pool = EnergyPool.deploy(
        energy_profile.address,
        energy_market.address,
        energy_price_oracle.address,
        {"from": deployer},
    )

    return energy_profile, energy_pool, energy_market
def test_simulate_energy_pool(setup):
    # Create an array of 24 numbers representing the energy production for each hour of the day
    energy_production = np.zeros(24)
    energy_production[8:20] = np.sin(
        np.linspace(0, np.pi, 12))*2*100  # Values between 0 and 2, peaking at noon

    energy_profile, energy_pool, energy_market = setup
    users = [accounts[i] for i in range(1, 2)]  # Create a list of 3 users

    # Set the EnergyPool contract address in the EnergyProfile contract
    energy_profile.setEnergyPoolContract(energy_pool.address, {"from": accounts[0]})

    # Register users as producers
    for user in users:
        energy_profile.registerUser(user, 1, "Location1", "Solar", {"from": user})

    # Simulate the energy commitment for every 10 minutes from 0h to 24h
    for hour in range(24):
        # Calculate the amount of committed energy based on the hour of the day
        committed_energy = energy_production[hour]

        for user in users:
            # Get tokenId for user
            tokenId = energy_profile.tokenOfOwnerByIndex(user, 0)

            # Create a commitment for user
            energy_profile.createCommitment(tokenId, committed_energy, True, 3600, {"from": user})

            # Approve the EnergyPool contract to manage the user's NFT
            energy_profile.approve(energy_pool.address, tokenId, {"from": user})

            # Deposit the EnergyProfile NFT into the EnergyPool
            energy_pool.deposit(tokenId, {"from": user})

            # Withdraw the EnergyProfile NFT from the EnergyPool
            energy_pool.withdraw(tokenId, {"from": user})


    # Plot the committed energy in the interval
    energyProduced_list = []
    current_interval_block_number_list = []
    for i in range(24):
        energyProduced, _, current_interval_block_number= energy_pool.intervals(i)
        current_interval_block_number_list.append(current_interval_block_number)
        energyProduced_list.append(energyProduced/100)
    plt.plot(range(23,-1,-1), energyProduced_list)
    plt.title("Committed Energy in the Interval")
    plt.xlabel("hours from 0 to 23")
    plt.ylabel("Committed Energy (kW)")
    plt.savefig("1day_committed_energy.png")
    plt.show()

    pdb.set_trace()
    print("Done")