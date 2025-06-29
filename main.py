import struct
import hashlib

class CompactSizeEncoder:
    """
    Encodes an integer into Bitcoin's CompactSize format.
    This format is used to indicate the length of following data.

    Encoding rules:
    - If value < 0xFD (253), it is encoded as a single byte.
    - If value <= 0xFFFF (65535), it is encoded as 0xFD followed by the 2-byte little-endian value.
    - If value <= 0xFFFFFFFF (4294967295), it is encoded as 0xFE followed by the 4-byte little-endian value.
    - If value > 0xFFFFFFFF, it is encoded as 0xFF followed by the 8-byte little-endian value.
    """
    def encode(self, value: int) -> bytes:
        """
        Encodes a given integer value into CompactSize bytes.

        Args:
            value (int): The integer to encode.

        Returns:
            bytes: The CompactSize byte representation.

        Raises:
            ValueError: If the value is negative or exceeds u64 max.
        """
        # TODO: Implement the CompactSize encoding logic here.
        # 1. Add validation for `value`: must be a non-negative integer and fit within u64 (0 to 18446744073709551615).
        #    Raise ValueError for invalid inputs.
        # 2. Use `if/elif/else` to check the `value` range against 0xFD, 0xFFFF, 0xFFFFFFFF.
        # 3. For each range, prepend the correct prefix byte (0xFD, 0xFE, 0xFF) if necessary.
        # 4. Convert the `value` to bytes using `.to_bytes()` with `length` and `byteorder='little'`.
        #    - For single byte, no prefix needed.
        #    - For 2-byte, use 2 for length.
        #    - For 4-byte, use 4 for length.
        #    - For 8-byte, use 8 for length.
        pass

class CompactSizeDecoder:
    """
    Decodes Bitcoin's CompactSize bytes into an integer.
    """
    def decode(self, data: bytes) -> tuple[int, int]:
        """
        Decodes a CompactSize integer from the beginning of a byte sequence.

        Args:
            data (bytes): The byte sequence to decode from.

        Returns:
            tuple[int, int]: A tuple containing the decoded integer value
                             and the number of bytes consumed.

        Raises:
            ValueError: If data is too short or has an invalid prefix.
        """
        # TODO: Implement the CompactSize decoding logic here.
        # 1. Check if `data` is empty. If so, raise ValueError ("Data is too short to decode CompactSize.").
        # 2. Get the `first_byte` from `data[0]`.
        # 3. Use `if/elif/else` to determine the length based on `first_byte`:
        #    - If `first_byte < 0xFD`: The value is the `first_byte` itself; 1 byte consumed.
        #    - If `first_byte == 0xFD`: Expect 2 more bytes. Check `len(data)` is at least 3.
        #      Convert `data[1:3]` to int using `int.from_bytes()` with `byteorder='little'`. 3 bytes consumed.
        #    - If `first_byte == 0xFE`: Expect 4 more bytes. Check `len(data)` is at least 5.
        #      Convert `data[1:5]` to int. 5 bytes consumed.
        #    - If `first_byte == 0xFF`: Expect 8 more bytes. Check `len(data)` is at least 9.
        #      Convert `data[1:9]` to int. 9 bytes consumed.
        # 4. Raise ValueError for `data` being too short for the indicated prefix.
        # 5. Return the decoded integer and the number of bytes consumed as a tuple.
        pass

class TransactionData:
    """
    A class to represent and manage simplified Bitcoin transaction data.
    Illustrates lists, dictionaries, tuples, unpacking, and various loop constructs.
    """
    def __init__(self, version: int = 1, lock_time: int = 0):
        self.version = version
        self.inputs = []  # List of dictionaries, each representing a transaction input
        self.outputs = [] # List of tuples, each representing a transaction output
        self.lock_time = lock_time
        self.metadata = {} # Dictionary for arbitrary transaction metadata

    def add_input(self, tx_id: str, vout_index: int, script_sig: str, sequence: int = 0xFFFFFFFF):
        """
        Adds a new transaction input using list.append() and a dictionary.

        Args:
            tx_id (str): The ID (hash) of the previous transaction.
            vout_index (int): The index of the output being spent in the previous transaction.
            script_sig (str): The unlocking script.
            sequence (int): The sequence number.
        """
        # TODO: Create a dictionary for the input and add to the `inputs` list.
        # TODO: Add a print statement confirming the input was added.
        pass

    def add_output(self, value_satoshi: int, script_pubkey: str):
        """
        Adds a new transaction output using list.append() and a tuple.

        Args:
            value_satoshi (int): The amount in satoshis.
            script_pubkey (str): The locking script.
        """
        # TODO: Create a tuple for the output and add to the `outputs` list.
        # TODO: Add a print statement confirming the output was added.
        pass

    def get_input_details(self) -> list[dict]:
        """
        Retrieves details of all transaction inputs.
        Demonstrates 'for' loop and 'enumerate'.

        Returns:
            list[dict]: A list of input details.
        """
        detailed_inputs = []
        print("\n--- Input Details (using for and enumerate) ---")
        # TODO: Iterate through `self.inputs` using a `for` loop with `enumerate` to get both index and input_data.
        # TODO: Inside the loop, print the input index.
        # TODO: Use multiple assignment/dictionary unpacking (e.g., `input_data.get(...)`) to extract
        #       `prev_txid`, `prev_vout`, and `script_sig` from `input_data`.
        # TODO: Print these extracted details.
        # TODO: Append a `copy` of the `input_data` dictionary to `detailed_inputs`.
        # TODO: Return `detailed_inputs`.
        pass

    def summarize_outputs(self, min_value: int = 0) -> tuple[int, int]:
        """
        Summarizes transaction outputs, skipping or breaking based on conditions.
        Demonstrates 'while', 'continue', and 'break' loops.

        Args:
            min_value (int): Minimum satoshi value for an output to be included in sum.

        Returns:
            tuple[int, int]: Total satoshis in valid outputs and count of valid outputs.
        """
        total_satoshi = 0
        valid_outputs_count = 0
        index = 0
        print("\n--- Summarizing Outputs (using while, continue, break) ---")
        # TODO: Use a `while` loop that continues as long as `index` is less than `len(self.outputs)`.
        # TODO: Inside the loop, unpack the current `value` and `script` from `self.outputs[index]` using tuple unpacking.
        # TODO: Implement a `continue` condition:
        #    - If `value` is not an integer or is negative, print a message and `continue` to the next iteration.
        # TODO: Implement another `continue` condition:
        #    - If `value` is less than `min_value`, print a message and `continue` to the next iteration.
        # TODO: If the output is valid, add `value` to `total_satoshi` and increment `valid_outputs_count`.
        # TODO: Print details of the included output.
        # TODO: Implement a `break` condition:
        #    - If `total_satoshi` exceeds a certain threshold (e.g., 1,000,000,000 satoshis), print a message and `break` out of the loop.
        # TODO: Increment `index` at the end of each iteration (before `continue`/`break` checks).
        # TODO: Return `(total_satoshi, valid_outputs_count)` as a tuple.
        pass

    def update_metadata(self, new_data: dict):
        """
        Updates the transaction metadata using dictionary methods.

        Args:
            new_data (dict): A dictionary of new metadata to add/update.
        """
        # TODO: Using dict.update() to merge new_data into metadata
        # TODO: Add a print statement showing the updated metadata.
        pass

    def get_metadata_value(self, key: str, default=None):
        """
        Retrieves a value from metadata using dict.get().
        """
        # TODO: Return the retrieved value.
        pass

    def get_transaction_header(self) -> tuple:
        """
        Returns core transaction header elements.
        Demonstrates simple tuple creation and returning.
        """
        # A simple tuple of header components
        # TODO: Create and return a tuple containing `version`, `length of inputs`, `length of outputs`, and `lock_time`.
        pass

    def set_transaction_header(self, version: int, num_inputs: int, num_outputs: int, lock_time: int):
        """
        Sets transaction header elements using multiple assignment.
        Note: num_inputs and num_outputs here are for demonstration of multiple assignment
        and wouldn't typically directly set list lengths in a real scenario.
        """
        # Multiple assignment for header elements
        # TODO: Use multiple assignment to set `version`, and `lock_time`.
        #       You can use `_` for `num_inputs` and `num_outputs` if you don't intend to use them.
        # TODO: Add a print statement confirming the attributes were set.
        pass

class UTXOSet:
    """
    Manages a set of Unspent Transaction Outputs (UTXOs).
    Illustrates Python's `set` data structure and its methods.

    UTXOs are represented as tuples: (transaction_id_hex, vout_index, amount_satoshi).
    """
    def __init__(self):
        self.utxos = set() # Set to store unique UTXO tuples

    def add_utxo(self, tx_id: str, vout_index: int, amount: int):
        """
        Adds a UTXO to the set.
        """
        # TODO: Create a UTXO tuple using tx_id, vout_index, amount.
        # TODO: Add this tuple to the set.
        # TODO: Add a print statement confirming the UTXO was added.
        pass

    def remove_utxo(self, tx_id: str, vout_index: int, amount: int) -> bool:
        """
        Removes a UTXO from the set if it exists.

        Returns:
            bool: True if removed, False otherwise.
        """
        # TODO: Create and remove the UTXO tuple from the set.
        pass

    def get_balance(self) -> int:
        """
        Calculates the total balance from all UTXOs in the set.
        """
        # TODO: Iterate through the utxos and return the total
        pass

    def find_sufficient_utxos(self, target_amount: int) -> set:
        """
        Finds a subset of UTXOs that sum up to at least the target amount.
        Demonstrates set operations (creating a new set).

        Args:
            target_amount (int): The amount needed.

        Returns:
            set: A set of UTXOs that fulfill the amount, or empty set if not possible.
        """
        # TODO: return set of UTXOs that fulfill the target_amount, or empty set if not possible.
        pass


    def get_total_utxo_count(self) -> int:
        """
        Returns the number of UTXOs in the set.
        Demonstrates `len()` on a set.
        """
        # TODO: Return the length of the utxos set
        pass

    def is_subset_of(self, other_utxo_set: 'UTXOSet') -> bool:
        """
        Checks if this UTXO set is a subset of another.
        Demonstrates set.issubset().
        """
        # TODO: check if is subset and return the result.
        pass

    def combine_utxos(self, other_utxo_set: 'UTXOSet') -> 'UTXOSet':
        """
        Combines two UTXO sets
        """
        # TODO: Return `combined_set`.
        pass

    def find_common_utxos(self, other_utxo_set: 'UTXOSet') -> 'UTXOSet':
        """
        Finds UTXOs common to two sets using set.intersection().
        """
        # TODO: Get the intersection of the two sets and Return the common_set
        pass

def generate_block_headers(
    prev_block_hash: str,
    merkle_root: str,
    timestamp: int,
    bits: int,
    start_nonce: int = 0,
    max_attempts: int = 1000
):
    """
    A generator function that simulates generating block headers by incrementing the nonce.
    This demonstrates the concept of proof-of-work attempts.

    Args:
        prev_block_hash (str): The hash of the previous block.
        merkle_root (str): The Merkle root of the transactions.
        timestamp (int): The block timestamp.
        bits (int): The target difficulty in compact form.
        start_nonce (int): The starting nonce.
        max_attempts (int): Maximum number of nonces to try.

    Yields:
        dict: A dictionary representing a potential block header, including the current nonce.
    """
    print(f"\n--- Generating Block Headers (using generator) ---")
    # TODO: Use a `while` loop that continues as long as `attempts < max_attempts`.
    # TODO: Inside the loop, create a dictionary `header_data` with keys like "version",
    #       "prev_block_hash", "merkle_root", "timestamp", "bits", and the current "nonce".
    # TODO: Simulate a hash calculation (e.g., using `hashlib.sha256` on a string representation of `header_data`).
    # TODO: Print the current attempt, nonce, and simulated hash prefix.
    # TODO: Use `yield header_data` to return the current header without exiting the function.
    # TODO: Increment `nonce` and `attempts`.
    # TODO: Add a conditional print statement (e.g., every 100 attempts) to show progress.
    pass