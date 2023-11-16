// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./EnergyProfile.sol";
import "./EnergyMarket.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV2V3Interface.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract EnergyPool is Ownable {
    // State variables here
    using Counters for Counters.Counter;
    Counters.Counter private _poolIdCounter;

        // Added explicit visibility to state variables
    EnergyProfile private _energyProfileContract;
    EnergyMarket private _energyMarketContract;
    AggregatorV2V3Interface private _energyPriceOracle;


    uint256 public totalEnergyCommittedProduction;
    uint256 public totalEnergyCommittedConsumption;
    uint256 public numberOfDeposits = 0;

    mapping(uint256 => uint256) public intervalEnergyCommittedProduced;
    mapping(uint256 => uint256) public intervalEnergyCommittedConsumed;
    mapping(uint256 => uint256) public intervalEnergyProduced;
    mapping(uint256 => uint256) public intervalEnergyConsumed;

    mapping(uint256 => bool) private _depositedNFTs;
    uint256 public intervalDuration = 295; //  295 blocks ~ 1 hour
    uint256 public current_interval_block_number;
    // Step 3: Constructor
    constructor(
    address energyProfileContractAddress,
    address energyMarketContractAddress,
    address energyPriceOracleAddress
    ){
    _energyProfileContract = EnergyProfile(energyProfileContractAddress);
    _energyMarketContract = EnergyMarket(energyMarketContractAddress);
    _energyPriceOracle = AggregatorV2V3Interface(energyPriceOracleAddress);
    current_interval_block_number = block.number;
    }
    struct Interval {
    uint256 energyCommittedProduction;
    uint256 energyCommittedConsumption;
    uint256 current_interval_block_number;
    uint256 energyProduced;
    uint256 energyConsumed;
    }
    Interval[24] public intervals;
//    create two struct for interval producer and consumer with Profile NFT ID and commitment index


    event Deposit(address indexed user, uint256 tokenId);
    event Withdraw(address indexed user, uint256 tokenId);
    event MarketPriceUpdated(uint256 newEnergyPrice);
    event ProductionMatched(uint256 indexed tokenId, uint256 energyAmount);
    event EnergyIntervalUpdated(uint256 indexed tokenId, uint256 totalEnergyCommittedProduction, uint256 totalEnergyCommittedConsumption, uint256 intervalEnergyProduced, uint256 intervalEnergyConsumed);


    // Step 4: Deposit function
    // Allows users to deposit their EnergyProfile NFTs into the pool
    function deposit(uint256 tokenId) public {
        require(IERC721(_energyProfileContract).ownerOf(tokenId) == msg.sender, "Not the owner of the token");

        EnergyProfile.Commitment[] memory commitments = _energyProfileContract.getUserCommitments(tokenId);

        for (uint i = 0; i < commitments.length; i++) {
            updateIntervalEnergy(tokenId, i);
            addCommitmentToMarketBufferAndProcess(tokenId, i);
        _depositedNFTs[tokenId] = true;
        }
        numberOfDeposits += 1;
        emit Deposit(msg.sender, tokenId);
    }
    function isDeposited(uint256 tokenId) public view returns (bool) {
        return _depositedNFTs[tokenId];
    }
    function updateCommitment(
        uint256 tokenId,
        uint256 energyAmount,
        bool isProduction,
        uint256 duration
    ) public {
        // Check if the sender is the original owner of the token
        require(
            EnergyProfile(_energyProfileContract).ownerOf(tokenId) == msg.sender && _depositedNFTs[tokenId],
            "Only the original owner of the token can update a commitment if the token is deposited in the EnergyPool"
        );

        // Call createCommitment on the EnergyProfile contract
        uint256 newCommitmentIndex = EnergyProfile(_energyProfileContract).createCommitment(tokenId, energyAmount, isProduction,
            duration);

        // Call updateIntervalEnergy function
        updateIntervalEnergy(tokenId, newCommitmentIndex);
    }

//  ----------------------- debug function, remove later
    function setCommitmentSettled(uint256 tokenId, uint256 commitmentIndex) public {
        _energyProfileContract.setCommitmentSettled(tokenId, commitmentIndex, true);
    }

//
//    // Step 5: Withdraw function
//    // Allows users to withdraw their EnergyProfile NFTs from the pool
//    function withdraw(uint256 tokenId) public {
//        require(IERC721(_energyProfileContract).ownerOf(tokenId) == msg.sender, "Not the owner of the token");
////        IERC721(_energyProfileContract).approve(address(0), tokenId);
//        numberOfDeposits--;
//        emit Withdraw(msg.sender, tokenId);
//        _depositedNFTs[tokenId] = false;
//    }

    function updateIntervalEnergy(uint256 tokenId, uint256 commitmentIndex) internal {
        EnergyProfile.UserData memory userData = _energyProfileContract.getUserProfile(tokenId);
        EnergyProfile.Commitment memory commitment = _energyProfileContract.getUserCommitments(tokenId)[commitmentIndex];

        // Check if the commitment has been processed by the energy pool
        require(!commitment.energy_pool_processed, "Commitment has already been processed by the energy pool");

        uint256 intervalBlockNumber = block.number - current_interval_block_number;

        if (intervalBlockNumber <intervalDuration) {
            if (commitment.isProduction) {
                totalEnergyCommittedProduction += commitment.energyAmount;
                intervals[0].energyCommittedProduction += commitment.energyAmount;
            } else {
                totalEnergyCommittedConsumption += commitment.energyAmount;
                intervals[0].energyCommittedConsumption += commitment.energyAmount;
            }
        } else {
            current_interval_block_number = block.number;
            Interval memory newInterval = Interval({
                energyCommittedProduction: commitment.isProduction ? commitment.energyAmount : 0,
                energyCommittedConsumption: !commitment.isProduction ? commitment.energyAmount : 0,
                current_interval_block_number: current_interval_block_number,
                energyProduced: 0,
                energyConsumed: 0

            });

            // Perform a circular shift to the right and overwrite the last item in the intervals list
            for (uint256 i = intervals.length - 1; i > 0; i--) {
                intervals[i] = intervals[i - 1];
            }

            // Replace the first interval with the new interval
            intervals[0] = newInterval;

            if (commitment.isProduction) {
                totalEnergyCommittedProduction += commitment.energyAmount;
            } else {
                totalEnergyCommittedConsumption += commitment.energyAmount;
            }
        }

        // Mark the commitment as processed by the energy pool
        _energyProfileContract.setCommitmentProcessed(tokenId, commitmentIndex, true);
    }


    // Helper function for the EnergyMarket contract to modify the energyProduced and energyConsumed
    // of the first interval in the intervals array.
    function updateIntervalEnergyByMarket(bool isProduction, uint256 energyAmount) public {
        // Only allow the EnergyMarket contract to call this function
        require(msg.sender == address(_energyMarketContract), "Only the EnergyMarket contract can update interval energy");

        if (isProduction) {
            intervals[0].energyProduced += energyAmount;
        } else {
            intervals[0].energyConsumed += energyAmount;
        }
    }


        // Add a commitment to the market buffer and process it
    function addCommitmentToMarketBufferAndProcess(uint256 profileNFTId, uint256 commitmentIndex) internal{
//         make it callable only by current contract
//        require(msg.sender == address(e), "Only the EnergyPool contract can add commitments to the market buffer");

        // Call the addCommitmentToBuffer function of the EnergyMarket contract
        _energyMarketContract.addCommitmentToBuffer(profileNFTId, commitmentIndex);

        // Call the process_buffer function of the EnergyMarket contract
        _energyMarketContract.process_buffer();
    }

    // Function to be called by a Chainlink oracle that activates the contract
    function oracleActivation() external {
        // Oracle activation logic here
    }


}
