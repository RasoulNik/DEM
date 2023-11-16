# tests/test_energy_profile.py
import pytest
import pdb
from brownie import (
    EnergyProfile,
    MockV3AggregatorEnergyProduced,
    MockV3AggregatorEnergyConsumed,
    MockV3AggregatorPrice,
    accounts,
    network,
    reverts,
)

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

    return energy_profile

def test_energy_production_commitment(setup):
    energy_profile = setup
    user1 = accounts[1]

    # Register user1
    energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1})

    # Get tokenId for user1
    tokenId = energy_profile.tokenOfOwnerByIndex(user1, 0)

    # Create energy profile for user1
    energy_profile.createCommitment(tokenId, 10 , True, 3600, {"from": user1})
    energy_profile.createCommitment(tokenId, 20, True, 3600, {"from": user1})
    energy_profile.createCommitment(tokenId, 30, True, 3600, {"from": user1})
    energy_profile.createCommitment(tokenId, 40, True, 3600, {"from": user1})

    # Check if the energy production commitment is successfully stored
    commitment_tuple = energy_profile.getUserCommitments(tokenId)[2]
    commitments_length = energy_profile.getCommitmentsLength(tokenId)
    # pdb.set_trace()
    # Map the tuple values to their corresponding struct field names
    commitment = {
        'energyAmount': commitment_tuple[0],
        'isProduction': commitment_tuple[1],
        'startTime': commitment_tuple[2],
        'duration': commitment_tuple[3],
        'settled': commitment_tuple[4],
        'energy_pool_processed': commitment_tuple[5],
        'energy_market_processed': commitment_tuple[6]
    }

    # pdb.set_trace()

    # Check the commitment fields
    assert commitment['energyAmount'] == 40
    assert commitment['isProduction'] == True
    assert commitment['settled'] == False
    assert commitment['energy_pool_processed'] == False
    assert commitment['energy_market_processed'] == False
    assert commitments_length == 3

    def test_only_owner_can_add_commitment(setup):
        energy_profile = setup
        user1 = accounts[1]
        user2 = accounts[2]

        # Register user1
        energy_profile.registerUser(user1, 10, "Location1", "Solar", {"from": user1})

        # Get tokenId for user1
        tokenId = energy_profile.tokenOfOwnerByIndex(user1, 0)

        # Create energy profile for user1
        energy_profile.createCommitment(tokenId, 10, True, 3600, {"from": user1})

        # Try to create a commitment for user1 by user2
        with reverts("Only the owner of the token can add a commitment"):
            energy_profile.createCommitment(tokenId, 20, True, 3600, {"from": user2})

