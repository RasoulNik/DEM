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
# def test_set_commitment_settled(setup):
#     energy_profile, energy_pool, energy_market = setup
#     user1 = accounts[1]
#     user2 = accounts[2]
#     # Register user1
#     # energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1})
#     energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1, "value": 0.1 * 10**18})
#     energy_profile.registerUser(user2, 10, "Location1", "Solar", {"from": user2, "value": 0.2 * 10**18})
#
#     print(energy_profile.getCommitmentsLength(0))
#     # Get tokenId for user1
#     tokenId = energy_profile.tokenOfOwnerByIndex(user1, 0)
#     tokenId2 = energy_profile.tokenOfOwnerByIndex(user2, 0)
#     # Create three commitments for user1
#     energy_profile.createCommitment(tokenId, 10, False, 195, {"from": user1})
#     energy_profile.createCommitment(tokenId2, 3, True, 195, {"from": user2})
#     energy_profile.createCommitment(tokenId2, 4, True, 195, {"from": user2})
#
#     # Approve the EnergyPool contract to manage the user's NFT
#     energy_profile.approve(energy_pool.address, tokenId, {"from": user1})
#     energy_profile.approve(energy_pool.address, tokenId2, {"from": user2})
#     # Deposit the EnergyProfile NFT into the EnergyPool
#
#     energy_pool.deposit(tokenId, {"from": user1})
#     energy_pool.deposit(tokenId2, {"from": user2})
#     print(energy_market.getBufferLength())  # Assumes you have implemented a getBufferLength function
#     print(energy_pool.intervals(0))
#     # pdb.set_trace()
#         # energy_profile.getUserCommitments(tokenId)
#         # # Set the first commitment status to settled
#         # energy_pool.setCommitmentSettled(tokenId, 0)
#         # # print energy_pool.intervals(0)
#         # print(energy_pool.intervals(0))
#         # # Create another commitment for user1
#         # energy_pool.updateCommitment(tokenId, 5, True, 195, {"from": user1})
#         # # energy_profile.createCommitment(tokenId, 5, True, 195, {"from": user1})
#         # # print energy_pool.intervals(0)
#         # print(energy_pool.intervals(0))
#         # Check if the first commitment is settled
#         # to tes this part the commitment should be a public array
#         # commitment = energy_profile._userCommitments(tokenId, 0)
#         # settled = commitment[4]  # assuming the `settled` field is at index 5
#         # energy_pool_processed = commitment[5]
#         # assert energy_pool_processed == True
#         # assert settled == False
#     # -----------------------------------
#     #  use settled commitment from energy market contract
#     # pdb.set_trace()
#     energy_market.settle_commitment({"from": user1})
#
#         # # -----------------------------------
#         # # Withdraw the EnergyProfile NFT from the EnergyPool
#         # energy_pool.withdraw(tokenId, {"from": user1})
#         # energy_profile.approve(ZERO_ADDRESS, tokenId, {"from": user1})
#         #
#         # # Check if the withdrawal was successful
#         # assert energy_profile.ownerOf(tokenId) == user1
#         # assert energy_profile.getApproved(tokenId) == ZERO_ADDRESS
def test_settle_commitment(setup):
    # load user 1 and 2 address from accounts
    user1 = network.accounts[1]
    user2 = network.accounts[2]
    value1 = 0.1
    value2 = 0.2
    # You might need to adjust this part to use the actual deployed instances of your contracts
    # energy_profile, energy_pool, energy_market = dem.energy_profile, dem.energy_pool, dem.energy_market
    energy_profile, energy_pool, energy_market = setup


    # Execute the operations
    energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1, "value": value1 * 10**18})
    energy_profile.registerUser(user2, 10, "Location1", "Solar", {"from": user2, "value": value2 * 10**18})

    tokenId1 = energy_profile.tokenOfOwnerByIndex(user1, 0)
    tokenId2 = energy_profile.tokenOfOwnerByIndex(user2, 0)

    energy_profile.createCommitment(tokenId1, 10, False, 195, {"from": user1})
    energy_profile.createCommitment(tokenId2, 3, True, 195, {"from": user2})
    energy_profile.createCommitment(tokenId2, 4, True, 195, {"from": user2})

    energy_profile.approve(energy_pool.address, tokenId1, {"from": user1})
    energy_profile.approve(energy_pool.address, tokenId2, {"from": user2})

    energy_pool.deposit(tokenId1, {"from": user1})
    energy_pool.deposit(tokenId2, {"from": user2})

    energy_market.settle_commitment({"from": user1})

# ---------------------------- working properly ----------------------------
# def test_add_commitment_to_buffer(setup):
#     energy_profile, energy_pool, energy_market = setup
#     deployer = accounts[0]
#     user = accounts[1]
#
#     # Register a user and create a commitment
#     energy_profile.registerUser(user.address, 1000, "San Francisco", "solar", {"from": user})
#     commitment_index = energy_profile.createCommitment(1, 10, True, 200, {"from": user})
#     tokenId = energy_profile.tokenOfOwnerByIndex(user, 0)
#
#      # check individual component in the process commitment function
#     # Add the commitment to the buffer
#     energy_market.addCommitmentToBuffer(tokenId, 0, {"from": deployer})
#     gas_estimate = energy_market.addCommitmentToBuffer.estimate_gas(0, 0, {"from": deployer})
#     # pdb.set_trace()
#     energy_market.check_expired_commitments({"from": energy_market.address})
#     # energy_profile.setMarketProcessed(tokenId, 0, True, {"from": energy_market.address})
#     energy_market.processCommitment(tokenId,0,{"from": energy_market.address})
#     #  get the commitment amd check that it is the same as the one we added
#     commitment = energy_profile.getUserCommitments(tokenId)
#     print(commitment)
#
#     # Check that the commitment was correctly added to the buffer
#     # pdb.set_trace()
#     buffer_length = energy_market.getBufferLength()  # Assumes you have implemented a getBufferLength function
#     assert buffer_length == 1


