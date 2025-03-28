// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract SimpleStorage {
    uint256 public storedNumber;

    function setNumber(uint256 _number) public {
        storedNumber = _number;
    }

    function getNumber() public view returns (uint256) {
        return storedNumber;
    }

    function deleteNumber() public {
        storedNumber = 0;
    } 
}