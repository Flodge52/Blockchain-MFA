// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract BMFAServer {
    uint256 public salt;
    uint256 public pinNumber; // Declare as a state variable

    
    /**
     * notice Updates the salt value, ensuring it's within a valid range.
     * param _userSalt The user-provided salt value.
     */
    function setSalt(uint256 _userSalt) public {
        salt = _userSalt % 9999;
    }

    /**
     * notice Generates a six-digit number based on the block timestamp and salt.
     * return A number between 100000 and 999999.
     */
    function generatePin() public {
        pinNumber = (block.timestamp % 900000) + 100000 + salt;
    }

    /**
     * @notice Returns the currently stored PIN number.
     */
    function getPin() public view returns (uint256) {
        return pinNumber;
    }
}