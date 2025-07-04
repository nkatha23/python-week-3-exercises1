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
        # 1. Add validation for `value`: must be a non-negative integer and fit within u64 (0 to 18446744073709551615).
        #    Raise ValueError for invalid inputs.
        if not isinstance(value, int) or value < 0:
            raise ValueError("Value must be a non-negative integer")
        
        if value > 18446744073709551615:  # u64 max
            raise ValueError("Value exceeds u64 maximum")
        
        # 2. Use `if/elif/else` to check the `value` range against 0xFD, 0xFFFF, 0xFFFFFFFF.
        if value < 0xFD:  # 253
            # Single byte encoding - no prefix needed
            return value.to_bytes(1, byteorder='little')
        elif value <= 0xFFFF:  # 65535
            # 2-byte encoding with 0xFD prefix
            return bytes([0xFD]) + value.to_bytes(2, byteorder='little')
        elif value <= 0xFFFFFFFF:  # 4294967295
            # 4-byte encoding with 0xFE prefix
            return bytes([0xFE]) + value.to_bytes(4, byteorder='little')
        else:
            # 8-byte encoding with 0xFF prefix
            return bytes([0xFF]) + value.to_bytes(8, byteorder='little')

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
        # 1. Check if `data` is empty. If so, raise ValueError ("Data is too short to decode CompactSize.").
        if not data:
            raise ValueError("Data is too short to decode CompactSize.")
        
        # 2. Get the `first_byte` from `data[0]`.
        first_byte = data[0]
        
        # 3. Use `if/elif/else` to determine the length based on `first_byte`:
        if first_byte < 0xFD:
            # The value is the `first_byte` itself; 1 byte consumed.
            return first_byte, 1
        elif first_byte == 0xFD:
            # Expect 2 more bytes. Check `len(data)` is at least 3.
            if len(data) < 3:
                raise ValueError("Data too short")
            # Convert `data[1:3]` to int using `int.from_bytes()` with `byteorder='little'`. 3 bytes consumed.
            value = int.from_bytes(data[1:3], byteorder='little')
            return value, 3
        elif first_byte == 0xFE:
            # Expect 4 more bytes. Check `len(data)` is at least 5.
            if len(data) < 5:
                raise ValueError("Data too short")
            # Convert `data[1:5]` to int. 5 bytes consumed.
            value = int.from_bytes(data[1:5], byteorder='little')
            return value, 5
        elif first_byte == 0xFF:
            # Expect 8 more bytes. Check `len(data)` is at least 9.
            if len(data) < 9:
                raise ValueError("Data too short")
            # Convert `data[1:9]` to int. 9 bytes consumed.
            value = int.from_bytes(data[1:9], byteorder='little')
            return value, 9
        else:
            raise ValueError(f"Invalid CompactSize prefix: {first_byte}")

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
        # Create a dictionary for the input and add to the `inputs` list.
        input_data = {
            'prev_txid': tx_id,
            'prev_vout': vout_index,
            'script_sig': script_sig,
            'sequence': sequence
        }
        self.inputs.append(input_data)
        # Add a print statement confirming the input was added.
        print(f"Added input: {tx_id}:{vout_index}")

    def add_output(self, value_satoshi: int, script_pubkey: str):
        """
        Adds a new transaction output using list.append() and a tuple.

        Args:
            value_satoshi (int): The amount in satoshis.
            script_pubkey (str): The locking script.
        """
        # Create a tuple for the output and add to the `outputs` list.
        output_data = (value_satoshi, script_pubkey)
        self.outputs.append(output_data)
        # Add a print statement confirming the output was added.
        print(f"Added output: {value_satoshi} satoshis")

    def get_input_details(self) -> list[dict]:
        """
        Retrieves details of all transaction inputs.
        Demonstrates 'for' loop and 'enumerate'.

        Returns:
            list[dict]: A list of input details.
        """
        detailed_inputs = []
        print("\n--- Input Details (using for and enumerate) ---")
        # Iterate through `self.inputs` using a `for` loop with `enumerate` to get both index and input_data.
        for index, input_data in enumerate(self.inputs):
            # Inside the loop, print the input index.
            print(f"Input {index}:")
            # Use multiple assignment/dictionary unpacking to extract details from `input_data`.
            prev_txid = input_data.get('prev_txid')
            prev_vout = input_data.get('prev_vout')
            script_sig = input_data.get('script_sig')
            # Print these extracted details.
            print(f"  Previous TXID: {prev_txid}")
            print(f"  Previous VOUT: {prev_vout}")
            print(f"  Script Sig: {script_sig}")
            # Append a `copy` of the `input_data` dictionary to `detailed_inputs`.
            detailed_inputs.append(input_data.copy())
        # Return `detailed_inputs`.
        return detailed_inputs

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
        # Use a `while` loop that continues as long as `index` is less than `len(self.outputs)`.
        while index < len(self.outputs):
            # Inside the loop, unpack the current `value` and `script` from `self.outputs[index]` using tuple unpacking.
            value, script = self.outputs[index]
            # Implement a `continue` condition:
            # If `value` is not an integer or is negative, print a message and `continue` to the next iteration.
            if not isinstance(value, int) or value < 0:
                print(f"Skipping invalid output at index {index}: {value}")
                index += 1
                continue
            # Implement another `continue` condition:
            # If `value` is less than `min_value`, print a message and `continue` to the next iteration.
            if value < min_value:
                print(f"Skipping output at index {index}: {value} < {min_value}")
                index += 1
                continue
            # If the output is valid, add `value` to `total_satoshi` and increment `valid_outputs_count`.
            total_satoshi += value
            valid_outputs_count += 1
            # Print details of the included output.
            print(f"Including output {index}: {value} satoshis")
            # Implement a `break` condition:
            # If `total_satoshi` exceeds a certain threshold (e.g., 1,000,000,000 satoshis), print a message and `break` out of the loop.
            if total_satoshi > 1000000000:  # 1 billion satoshis
                print(f"Total satoshis exceeded 1 Billion. Breaking summarization.")
                break
            # Increment `index` at the end of each iteration.
            index += 1
        # Return `(total_satoshi, valid_outputs_count)` as a tuple.
        return (total_satoshi, valid_outputs_count)

    def update_metadata(self, new_data: dict):
        """
        Updates the transaction metadata using dictionary methods.

        Args:
            new_data (dict): A dictionary of new metadata to add/update.
        """
        # Using dict.update() to merge new_data into metadata
        self.metadata.update(new_data)
        # Add a print statement showing the updated metadata.
        print(f"Updated metadata: {self.metadata}")

    def get_metadata_value(self, key: str, default=None):
        """
        Retrieves a value from metadata using dict.get().
        """
        # Return the retrieved value.
        return self.metadata.get(key, default)

    def get_transaction_header(self) -> tuple:
        """
        Returns core transaction header elements.
        Demonstrates simple tuple creation and returning.
        """
        # Create and return a tuple containing `version`, `length of inputs`, `length of outputs`, and `lock_time`.
        return (self.version, len(self.inputs), len(self.outputs), self.lock_time)

    def set_transaction_header(self, version: int, num_inputs: int, num_outputs: int, lock_time: int):
        """
        Sets transaction header elements using multiple assignment.
        Note: num_inputs and num_outputs here are for demonstration of multiple assignment
        and wouldn't typically directly set list lengths in a real scenario.
        """
        # Multiple assignment for header elements
        # Use multiple assignment to set `version`, and `lock_time`.
        self.version, _, _, self.lock_time = version, num_inputs, num_outputs, lock_time
        # Add a print statement confirming the attributes were set.
        print(f"Set header via multiple assignment: version={self.version}, lock_time={self.lock_time}")

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
        # Create a UTXO tuple using tx_id, vout_index, amount.
        utxo_tuple = (tx_id, vout_index, amount)
        # Add this tuple to the set.
        self.utxos.add(utxo_tuple)
        # Add a print statement confirming the UTXO was added.
        print(f"Added UTXO: {tx_id}:{vout_index} - {amount} satoshis")

    def remove_utxo(self, tx_id: str, vout_index: int, amount: int) -> bool:
        """
        Removes a UTXO from the set if it exists.

        Returns:
            bool: True if removed, False otherwise.
        """
        # Create and remove the UTXO tuple from the set.
        utxo_tuple = (tx_id, vout_index, amount)
        if utxo_tuple in self.utxos:
            self.utxos.remove(utxo_tuple)
            return True
        return False

    def get_balance(self) -> int:
        """
        Calculates the total balance from all UTXOs in the set.
        """
        # Iterate through the utxos and return the total
        total = 0
        for tx_id, vout_index, amount in self.utxos:
            total += amount
        return total

    def find_sufficient_utxos(self, target_amount: int) -> set:
        """
        Finds a subset of UTXOs that sum up to at least the target amount.
        Demonstrates set operations (creating a new set).

        Args:
            target_amount (int): The amount needed.

        Returns:
            set: A set of UTXOs that fulfill the amount, or empty set if not possible.
        """
        # Return set of UTXOs that fulfill the target_amount, or empty set if not possible.
        selected_utxos = set()
        current_amount = 0
        
        for utxo in self.utxos:
            tx_id, vout_index, amount = utxo
            selected_utxos.add(utxo)
            current_amount += amount
            if current_amount >= target_amount:
                print(f"Found sufficient UTXOs for target amount {target_amount}")
                return selected_utxos
        
        # If we can't reach the target amount, return empty set
        if current_amount < target_amount:
            return set()
        return selected_utxos

    def get_total_utxo_count(self) -> int:
        """
        Returns the number of UTXOs in the set.
        Demonstrates `len()` on a set.
        """
        # Return the length of the utxos set
        return len(self.utxos)

    def is_subset_of(self, other_utxo_set: 'UTXOSet') -> bool:
        """
        Checks if this UTXO set is a subset of another.
        Demonstrates set.issubset().
        """
        # Check if is subset and return the result.
        return self.utxos.issubset(other_utxo_set.utxos)

    def combine_utxos(self, other_utxo_set: 'UTXOSet') -> 'UTXOSet':
        """
        Combines two UTXO sets
        """
        # Return `combined_set`.
        combined_set = UTXOSet()
        combined_set.utxos = self.utxos.union(other_utxo_set.utxos)
        return combined_set

    def find_common_utxos(self, other_utxo_set: 'UTXOSet') -> 'UTXOSet':
        """
        Finds UTXOs common to two sets using set.intersection().
        """
        # Get the intersection of the two sets and Return the common_set
        common_set = UTXOSet()
        common_set.utxos = self.utxos.intersection(other_utxo_set.utxos)
        return common_set

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
    nonce = start_nonce
    attempts = 0
    
    # Use a `while` loop that continues as long as `attempts < max_attempts`.
    while attempts < max_attempts:
        # Inside the loop, create a dictionary `header_data` with keys like "version",
        # "prev_block_hash", "merkle_root", "timestamp", "bits", and the current "nonce".
        header_data = {
            "version": 1,
            "prev_block_hash": prev_block_hash,
            "merkle_root": merkle_root,
            "timestamp": timestamp,
            "bits": bits,
            "nonce": nonce
        }
        
        # Simulate a hash calculation (e.g., using `hashlib.sha256` on a string representation of `header_data`).
        header_str = str(header_data)
        simulated_hash = hashlib.sha256(header_str.encode()).hexdigest()
        
        # Print the current attempt, nonce, and simulated hash prefix.
        print(f"Attempt {attempts + 1}: Nonce {nonce}, Hash: {simulated_hash[:8]}...")
        
        # Use `yield header_data` to return the current header without exiting the function.
        yield header_data
        
        # Increment `nonce` and `attempts`.
        nonce += 1
        attempts += 1
        
        # Add a conditional print statement (e.g., every 100 attempts) to show progress.
        if attempts % 100 == 0 and attempts > 0:
            print(f"... {attempts} attempts made ...")

# Example usage and testing
if __name__ == "__main__":
    # Test CompactSize encoder/decoder
    print("=== Testing CompactSize Encoder/Decoder ===")
    encoder = CompactSizeEncoder()
    decoder = CompactSizeDecoder()
    
    test_values = [0, 252, 253, 65535, 65536, 4294967295, 4294967296]
    for value in test_values:
        try:
            encoded = encoder.encode(value)
            decoded_value, bytes_consumed = decoder.decode(encoded)
            print(f"Value: {value}, Encoded: {encoded.hex()}, Decoded: {decoded_value}, Bytes: {bytes_consumed}")
        except ValueError as e:
            print(f"Error with value {value}: {e}")
    
    # Test TransactionData
    print("\n=== Testing TransactionData ===")
    tx = TransactionData(version=2, lock_time=500000)
    
    # Add some inputs and outputs
    tx.add_input("abc123", 0, "scriptSig1", 0xFFFFFFFF)
    tx.add_input("def456", 1, "scriptSig2", 0xFFFFFFFE)
    tx.add_output(100000000, "scriptPubKey1")  # 1 BTC
    tx.add_output(50000000, "scriptPubKey2")   # 0.5 BTC
    tx.add_output(-10000, "invalid_output")    # Invalid output
    
    # Test methods
    tx.get_input_details()
    total_sats, valid_count = tx.summarize_outputs(min_value=10000)
    print(f"Total satoshis: {total_sats}, Valid outputs: {valid_count}")
    
    tx.update_metadata({"fee": 1000, "size": 250})
    print(f"Fee: {tx.get_metadata_value('fee')}")
    
    header = tx.get_transaction_header()
    print(f"Transaction header: {header}")
    
    tx.set_transaction_header(3, 2, 2, 600000)
    
    # Test UTXOSet
    print("\n=== Testing UTXOSet ===")
    utxo_set1 = UTXOSet()
    utxo_set1.add_utxo("tx1", 0, 100000)
    utxo_set1.add_utxo("tx2", 1, 200000)
    utxo_set1.add_utxo("tx3", 0, 50000)
    
    print(f"Total balance: {utxo_set1.get_balance()}")
    print(f"UTXO count: {utxo_set1.get_total_utxo_count()}")
    
    sufficient_utxos = utxo_set1.find_sufficient_utxos(150000)
    print(f"Sufficient UTXOs for 150000: {sufficient_utxos}")
    
    utxo_set2 = UTXOSet()
    utxo_set2.add_utxo("tx1", 0, 100000)
    utxo_set2.add_utxo("tx4", 0, 300000)
    
    combined = utxo_set1.combine_utxos(utxo_set2)
    print(f"Combined UTXO count: {combined.get_total_utxo_count()}")
    
    common = utxo_set1.find_common_utxos(utxo_set2)
    print(f"Common UTXOs: {common.utxos}")
    
    # Test generator
    print("\n=== Testing Block Header Generator ===")
    header_gen = generate_block_headers(
        prev_block_hash="0000000000000000000000000000000000000000000000000000000000000000",
        merkle_root="abc123def456",
        timestamp=1640995200,
        bits=0x1d00ffff,
        start_nonce=0,
        max_attempts=5
    )
    
    for i, header in enumerate(header_gen):
        print(f"Generated header {i+1}: {header}")
        if i >= 2:  # Only show first 3 headers
            break
    
    print("\n=== All tests completed successfully! ===")