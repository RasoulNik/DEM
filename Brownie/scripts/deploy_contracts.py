from brownie import (
    EnergyProfile,
    EnergyPool,
    EnergyMarket,
    MockV3AggregatorEnergyProduced,
    MockV3AggregatorEnergyConsumed,
    MockV3AggregatorPrice,
    accounts,
    network,
)

def main():
    # Load the default account from the local Ganache
    deployer = accounts[0]

    # Deploy the MockV3Aggregator contracts
    energy_produced_oracle = MockV3AggregatorEnergyProduced.deploy(18, 1000000000, {"from": deployer})
    energy_consumed_oracle = MockV3AggregatorEnergyConsumed.deploy(18, 900000000, {"from": deployer})
    energy_price_oracle = MockV3AggregatorPrice.deploy(18, 2000, {"from": deployer})

    # Deploy the EnergyProfile contract
    energy_profile = EnergyProfile.deploy(
        energy_produced_oracle.address,
        energy_consumed_oracle.address,
        energy_price_oracle.address,
        {"from": deployer},
    )

    # Deploy the EnergyMarket contract
    energy_market = EnergyMarket.deploy({"from": deployer})

    # Deploy the EnergyPool contract
    energy_pool = EnergyPool.deploy(
        energy_profile.address,
        energy_market.address,
        energy_price_oracle.address,
        {"from": deployer},
    )

    # Set the EnergyPool contract address in the EnergyProfile contract
    energy_profile.setEnergyPoolContract(energy_pool.address, {"from": deployer})

    print(f"EnergyProfile deployed at: {energy_profile.address}")
    print(f"EnergyMarket deployed at: {energy_market.address}")
    print(f"EnergyPool deployed at: {energy_pool.address}")
    print(f"MockV3AggregatorEnergyProduced deployed at: {energy_produced_oracle.address}")
    print(f"MockV3AggregatorEnergyConsumed deployed at: {energy_consumed_oracle.address}")
    print(f"MockV3AggregatorPrice deployed at: {energy_price_oracle.address}")
