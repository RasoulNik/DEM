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

    energy_market = EnergyMarket.deploy(energy_profile.address,{"from": deployer})

    energy_pool = EnergyPool.deploy(
        energy_profile.address,
        energy_market.address,
        energy_price_oracle.address,
        {"from": deployer},
    )
    # set the energy pool contract address in the energy profile contract
    energy_profile.setEnergyPoolContract(energy_pool.address, {"from": deployer})
    energy_market.setEnergyPoolContract(energy_pool.address, {"from": deployer})
    return energy_profile, energy_pool, energy_market

def test_deposit_withdraw(setup):
    energy_profile, energy_pool, energy_market = setup
    user1 = accounts[1]

    # Register user1
    energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1})

    # Get tokenId for user1
    tokenId = energy_profile.tokenOfOwnerByIndex(user1, 0)

    # Approve the EnergyPool contract to manage the user's NFT
    energy_profile.approve(energy_pool.address, tokenId, {"from": user1})

    # Deposit the EnergyProfile NFT into the EnergyPool
    energy_pool.deposit(tokenId, {"from": user1})

    # Check if the deposit was successful
    assert energy_profile.ownerOf(tokenId) == user1
    assert energy_profile.getApproved(tokenId) == energy_pool.address

    # Withdraw the EnergyProfile NFT from the EnergyPool

    energy_pool.withdraw(tokenId, {"from": user1})
    energy_profile.approve(ZERO_ADDRESS, tokenId, {"from": user1})
    # Check if the withdrawal was successful
    assert energy_profile.ownerOf(tokenId) == user1
    assert energy_profile.getApproved(tokenId) == ZERO_ADDRESS



# def test_update_interval_energy(setup):
#     energy_profile, energy_pool, energy_market = setup
#     user1 = accounts[1]
#     # Set the EnergyPool contract address in the EnergyProfile contract
#     energy_profile.setEnergyPoolContract(energy_pool.address, {"from": accounts[0]})
#
#     # Register user1 as a producer
#     energy_profile.registerUser(user1, 1, "Location1", "Solar", {"from": user1})
#
#     # Get tokenId for user1
#     tokenId = energy_profile.tokenOfOwnerByIndex(user1, 0)
#
#     # Create a commitment for user1
#     energy_profile.createCommitment(tokenId, 2, True, 3600, {"from": user1})
#     energy_profile.createCommitment(tokenId, 3, True, 3600, {"from": user1})
#
#     # Approve the EnergyPool contract to manage the user's NFT
#     energy_profile.approve(energy_pool.address, tokenId, {"from": user1})
#
#     # Deposit the EnergyProfile NFT into the EnergyPool
#     energy_pool.deposit(tokenId, {"from": user1})
#
#     # Calculate the current interval
#     current_interval = chain.time() // energy_pool.intervalDuration()
#
#     # Check if the updateIntervalEnergy function updated the values correctly
#     assert energy_pool.totalEnergyProduced() == 5
#     pdb.set_trace()
#     assert energy_pool.intervalEnergyProduced(current_interval) == 3
#     assert energy_pool.totalEnergyConsumed() == 0
#     assert energy_pool.intervalEnergyConsumed(current_interval) == 0

    # Withdraw the EnergyProfile NFT from the EnergyPool


def test_set_commitment_settled(setup):
    energy_profile, energy_pool, energy_market = setup
    user1 = accounts[1]

    # Register user1
    energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1})

    # Get tokenId for user1
    tokenId = energy_profile.tokenOfOwnerByIndex(user1, 0)

    # Create three commitments for user1
    energy_profile.createCommitment(tokenId, 20, True, 195, {"from": user1})
    energy_profile.createCommitment(tokenId, 3, True, 195, {"from": user1})
    energy_profile.createCommitment(tokenId, 4, True, 195, {"from": user1})

    # Approve the EnergyPool contract to manage the user's NFT
    energy_profile.approve(energy_pool.address, tokenId, {"from": user1})
    # pdb.set_trace()
    # Deposit the EnergyProfile NFT into the EnergyPool
    pdb.set_trace()
    # energy_market.addCommitmentToBuffer(1, 1, {"from": user1})
    buffer_length = energy_market.getBufferLength()  # Assumes you have implemented a getBufferLength function
    energy_pool.deposit(tokenId, {"from": user1})

    # Set the first commitment status to settled
    energy_pool.setCommitmentSettled(tokenId, 0)
    # print energy_pool.intervals(0)
    print(energy_pool.intervals(0))
    # Create another commitment for user1
    energy_pool.updateCommitment(tokenId, 5, True, 195, {"from": user1})
    # energy_profile.createCommitment(tokenId, 5, True, 195, {"from": user1})
    # print energy_pool.intervals(0)
    print(energy_pool.intervals(0))
    # Check if the first commitment is settled

    commitment = energy_profile._userCommitments(tokenId, 0)
    settled = commitment[4]  # assuming the `settled` field is at index 5
    energy_pool_processed = commitment[5]
    assert energy_pool_processed == True
    assert settled == False
    # Withdraw the EnergyProfile NFT from the EnergyPool
    energy_pool.withdraw(tokenId, {"from": user1})

    # Check if the withdrawal was successful
    assert energy_profile.ownerOf(tokenId) == user1
    assert energy_profile.getApproved(tokenId) == ZERO_ADDRESS

#  working properly  nad passed
# def test_plot_interval_energy(setup):
#     energy_profile, energy_pool, energy_market = setup
#     users = [accounts[i] for i in range(1, 10)]  # Create a list of 24 users
#
#     # Set the EnergyPool contract address in the EnergyProfile contract
#     energy_profile.setEnergyPoolContract(energy_pool.address, {"from": accounts[0]})
#
#     # Register users as producers
#     for user in users:
#         energy_profile.registerUser(user, 1, "Location1", "Solar", {"from": user})
#
#         # Get tokenId for user
#         tokenId = energy_profile.tokenOfOwnerByIndex(user, 0)
#
#         # Create a commitment for user
#         kw_commitment1 = random.randint(1, 10)
#         kw_commitment2 = random.randint(1, 10)
#         energy_profile.createCommitment(tokenId, kw_commitment1, True, 3600, {"from": user})
#         energy_profile.createCommitment(tokenId, kw_commitment2, True, 3600, {"from": user})
#
#         # Approve the EnergyPool contract to manage the user's NFT
#         energy_profile.approve(energy_pool.address, tokenId, {"from": user})
#
#         # Deposit the EnergyProfile NFT into the EnergyPool
#         energy_pool.deposit(tokenId, {"from": user})
#         intervalBlockNumber = chain[-1].number - energy_pool.current_interval_block_number()
#         print(f"Interval Block Number for user {user}: {intervalBlockNumber}")
#
#     # Check if the updateIntervalEnergy function updated the values correctly
#     energyProduced, energyConsumed, _ = energy_pool.intervals(0)
#     #  plot the energy produced and consumed for each interval
#     energyProduced_list = []
#     energyConsumed_list = []
#     current_interval_block_number_list = []
#     for i in range(23, -1, -1):
#         energyProduced, energyConsumed, current_interval_block_number = energy_pool.intervals(i)
#         energyProduced_list.append(energyProduced)
#         energyConsumed_list.append(energyConsumed)
#         current_interval_block_number_list.append(current_interval_block_number)
#     intervals_index = list(range(-23, 1))
#     plt.plot(intervals_index,energyProduced_list, label="Energy Committed Produced")
#     plt.plot(intervals_index,energyConsumed_list, label="Energy Committed Consumed")
#     # plt.plot(intervals_index,current_interval_block_number_list, label="Current Interval Block Number")
#     plt.legend()
#     plt.title("Energy committed Produced and Consumed for each interval (kWh)")
#     plt.xlabel("Interval Index")
#     plt.ylabel("Energy (kWh)")
#     plt.savefig("energy_committed_produced_consumed.png")
#     plt.show()
#     # pdb.set_trace()
#     print(energy_pool.intervals(0), energy_pool.intervals(1), energy_pool.intervals(2))
# --------------------------------------------------------------
    # assert energy_pool.totalEnergyProduced() == 15
    #
    # assert energyProduced == 5
    # assert energy_pool.totalEnergyConsumed() == 0
    # assert energyConsumed == 0
    #
    # # Withdraw the EnergyProfile NFT from the EnergyPool
    # energy_pool.withdraw(tokenId, {"from": user1})
    # energy_profile.approve(ZERO_ADDRESS, tokenId, {"from": user1})
    #
    # # Check if the withdrawal was successful
    # assert energy_profile.ownerOf(tokenId) == user1
    # assert energy_profile.getApproved(tokenId) == ZERO_ADDRESS




