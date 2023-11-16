# tests/test_energy_pool.py
import pytest
import pdb
import flask
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
from brownie import Wei
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

@pytest.fixture(scope="module")
def setup():
    deployer = accounts[0]

    energy_produced_oracle = MockV3AggregatorEnergyProduced.deploy(18, 1000000000, {"from": deployer})
    energy_consumed_oracle = MockV3AggregatorEnergyConsumed.deploy(18, 900000000, {"from": deployer})
    energy_price_oracle = MockV3AggregatorPrice.deploy(18, 1 * 10**14, {"from": deployer})

    energy_profile = EnergyProfile.deploy(
        energy_produced_oracle.address,
        energy_consumed_oracle.address,
        energy_price_oracle.address,
        {"from": deployer},
    )

    energy_market = EnergyMarket.deploy(energy_profile.address,{"from": deployer})

    energy_pool = EnergyPool.deploy(
        energy_profile.address,
        energy_market.address,
        energy_price_oracle.address,
        {"from": deployer},
    )
    # set the energy pool contract address in the energy profile contract
    energy_profile.setEnergyPoolContract(energy_pool.address, {"from": deployer})
    energy_profile.setEnergyMarketContract(energy_market.address, {"from": deployer})

    energy_market.setEnergyPoolContract(energy_pool.address, {"from": deployer})
    return energy_profile, energy_pool, energy_market
import json

def test_set_commitment_settled(setup):
    energy_profile, energy_pool, energy_market = setup
    gas_used = {}
    num_users = 9

    # Register users and keep track of the gas used
    for i in range(1, num_users+1):
        user = accounts[i]
        tx = energy_profile.registerUser(user, 10, "Location1", "Solar", {"from": user, "value": 0.1 * 10**18})
        gas_used[f"registerUser {i}"] = tx.gas_used

    # Get tokenId for each user
    tokenIds = [energy_profile.tokenOfOwnerByIndex(user, 0) for user in accounts[1:num_users+1]]

    # Create commitments for each user and keep track of the gas used
    for i, tokenId in enumerate(tokenIds, start=1):
        user = accounts[i]
        tx = energy_profile.createCommitment(tokenId, 10, False, 195, {"from": user})
        gas_used[f"createCommitment {i}"] = tx.gas_used

    # Approve the EnergyPool contract to manage the user's NFT and keep track of the gas used
    for i, tokenId in enumerate(tokenIds, start=1):
        user = accounts[i]
        tx = energy_profile.approve(energy_pool.address, tokenId, {"from": user})
        gas_used[f"approve {i}"] = tx.gas_used

    # Deposit the EnergyProfile NFT into the EnergyPool and keep track of the gas used
    for i, tokenId in enumerate(tokenIds, start=1):
        user = accounts[i]
        tx = energy_pool.deposit(tokenId, {"from": user})
        gas_used[f"deposit {i}"] = tx.gas_used

    # Call settle_commitment and keep track of the gas used
    user1 = accounts[1]
    tx = energy_market.settle_commitment({"from": user1})
    gas_used["settle_commitment"] = tx.gas_used

    # Add number of users to the data
    gas_used["num_users"] = num_users

    # Save the gas used for each operation to disk
    filename = f'gas_used_{num_users}_users.json'
    with open(filename, 'w') as f:
        json.dump(gas_used, f)
    # pdb.set_trace()