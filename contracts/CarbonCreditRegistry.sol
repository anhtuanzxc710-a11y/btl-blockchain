// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Amounts are integers in units of 0.001 tCO2e.
/// @dev The regulator records new allocation for the period, as calculated off-chain.
contract CarbonCreditRegistry {
    address public immutable regulator;
    address public immutable verifier;
    uint32 public currentPeriod = 1;

    struct Quota {
        bool isSet;
        uint256 allocated;
        uint256 offsetUsed;
    }

    struct Lot {
        bytes32 projectId;
        address owner;
        uint256 issuedAmount;
        uint256 remaining;
        bytes32 mrvHash;
    }

    mapping(uint32 => mapping(address => Quota)) private quotas;
    mapping(bytes32 => Lot) private lots;
    mapping(bytes32 => bool) public usedMrvHash;

    error NotRegulator();
    error NotVerifier();
    error RolesMustDiffer();
    error InvalidPeriod();
    error ZeroAddress();
    error EmptySerial();
    error EmptyProjectId();
    error ZeroAmount();
    error EmptyMrvHash();
    error QuotaAlreadySet();
    error QuotaNotSet();
    error LotNotFound();
    error NotLotOwner();
    error DuplicateSerial();
    error DuplicateMrvHash();
    error InsufficientBalance();
    error OffsetCapExceeded();

    event PeriodOpened(uint32 indexed period);
    event QuotaSet(uint32 indexed period, address indexed company, uint256 allocated);
    event CreditIssued(bytes32 indexed serial, bytes32 indexed projectId, address indexed owner,
                       uint256 amount, bytes32 mrvHash);
    event OffsetRecorded(uint32 indexed period, address indexed company, bytes32 indexed serial,
                         uint256 amount);

    constructor(address verifier_) {
        regulator = msg.sender;
        if (verifier_ == address(0)) revert ZeroAddress();
        if (verifier_ == regulator) revert RolesMustDiffer();
        verifier = verifier_;
        emit PeriodOpened(currentPeriod);
    }

    modifier onlyRegulator() {
        if (msg.sender != regulator) revert NotRegulator();
        _;
    }

    function advancePeriod(uint32 nextPeriod) external onlyRegulator {
        if (nextPeriod <= currentPeriod) revert InvalidPeriod();
        currentPeriod = nextPeriod;
        emit PeriodOpened(nextPeriod);
    }

    function setQuota(uint32 period, address company, uint256 allocated) external onlyRegulator {
        if (period != currentPeriod) revert InvalidPeriod();
        if (company == address(0)) revert ZeroAddress();
        Quota storage quota = quotas[period][company];
        if (quota.isSet) revert QuotaAlreadySet();
        quota.isSet = true;
        quota.allocated = allocated;
        emit QuotaSet(period, company, allocated);
    }

    function mintVerifiedCredit(bytes32 serial, bytes32 projectId, address owner,
                                uint256 amount, bytes32 mrvHash) external {
        if (msg.sender != verifier) revert NotVerifier();
        if (serial == bytes32(0)) revert EmptySerial();
        if (projectId == bytes32(0)) revert EmptyProjectId();
        if (owner == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (mrvHash == bytes32(0)) revert EmptyMrvHash();
        if (lots[serial].owner != address(0)) revert DuplicateSerial();
        if (usedMrvHash[mrvHash]) revert DuplicateMrvHash();

        lots[serial] = Lot(projectId, owner, amount, amount, mrvHash);
        usedMrvHash[mrvHash] = true;
        emit CreditIssued(serial, projectId, owner, amount, mrvHash);
    }

    function recordOffset(uint32 period, bytes32 serial, uint256 amount) external {
        if (period != currentPeriod) revert InvalidPeriod();
        Lot storage lot = lots[serial];
        if (lot.owner == address(0)) revert LotNotFound();
        if (msg.sender != lot.owner) revert NotLotOwner();
        Quota storage quota = quotas[period][msg.sender];
        if (!quota.isSet) revert QuotaNotSet();
        if (amount == 0) revert ZeroAmount();
        if (amount > lot.remaining) revert InsufficientBalance();
        if (amount > _cap(quota.allocated) - quota.offsetUsed) revert OffsetCapExceeded();

        lot.remaining -= amount;
        quota.offsetUsed += amount;
        emit OffsetRecorded(period, msg.sender, serial, amount);
    }

    function quotaStatus(uint32 period, address company) external view returns (
        bool isSet, uint256 allocated, uint256 cap, uint256 offsetUsed
    ) {
        Quota storage quota = quotas[period][company];
        return (quota.isSet, quota.allocated, _cap(quota.allocated), quota.offsetUsed);
    }

    function lotStatus(bytes32 serial) external view returns (
        bytes32 projectId, address owner, uint256 issuedAmount, uint256 remaining, bytes32 mrvHash
    ) {
        Lot storage lot = lots[serial];
        if (lot.owner == address(0)) revert LotNotFound();
        return (lot.projectId, lot.owner, lot.issuedAmount, lot.remaining, lot.mrvHash);
    }

    function _cap(uint256 allocated) private pure returns (uint256) {
        // floor(allocated * 30 / 100), including allocations near uint256.max.
        return (allocated / 10) * 3 + ((allocated % 10) * 3) / 10;
    }
}
