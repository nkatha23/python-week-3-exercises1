import unittest
from main import *
import io
import sys
import hashlib

class TestCompactSize(unittest.TestCase):
    def setUp(self):
        self.encoder = CompactSizeEncoder()
        self.decoder = CompactSizeDecoder()

    def test_encode_decode_single_byte(self):
        values = [0, 1, 127, 252]
        for val in values:
            encoded = self.encoder.encode(val)
            self.assertEqual(len(encoded), 1)
            decoded_val, consumed = self.decoder.decode(encoded)
            self.assertEqual(decoded_val, val)
            self.assertEqual(consumed, 1)

    def test_encode_decode_two_bytes(self):
        values = [253, 254, 65535] # 0xFD to 0xFFFF
        for val in values:
            encoded = self.encoder.encode(val)
            self.assertEqual(len(encoded), 3) # 1 byte prefix + 2 bytes value
            self.assertEqual(encoded[0], 0xFD)
            decoded_val, consumed = self.decoder.decode(encoded)
            self.assertEqual(decoded_val, val)
            self.assertEqual(consumed, 3)

    def test_encode_decode_four_bytes(self):
        values = [65536, 65537, 4294967295] # 0x10000 to 0xFFFFFFFF
        for val in values:
            encoded = self.encoder.encode(val)
            self.assertEqual(len(encoded), 5) # 1 byte prefix + 4 bytes value
            self.assertEqual(encoded[0], 0xFE)
            decoded_val, consumed = self.decoder.decode(encoded)
            self.assertEqual(decoded_val, val)
            self.assertEqual(consumed, 5)

    def test_encode_decode_eight_bytes(self):
        values = [4294967296, 0xFFFFFFFFFFFFFFFF] # 0x100000000 to max u64
        for val in values:
            encoded = self.encoder.encode(val)
            self.assertEqual(len(encoded), 9) # 1 byte prefix + 8 bytes value
            self.assertEqual(encoded[0], 0xFF)
            decoded_val, consumed = self.decoder.decode(encoded)
            self.assertEqual(decoded_val, val)
            self.assertEqual(consumed, 9)

    def test_decode_insufficient_data(self):
        with self.assertRaisesRegex(ValueError, "Data too short"):
            self.decoder.decode(b'\xfd\x01') # Needs 3 bytes, got 2
        with self.assertRaisesRegex(ValueError, "Data too short"):
            self.decoder.decode(b'\xfe\x01\x02\x03') # Needs 5 bytes, got 4
        with self.assertRaisesRegex(ValueError, "Data too short"):
            self.decoder.decode(b'\xff' + b'\x00'*7) # Needs 9 bytes, got 8
        with self.assertRaisesRegex(ValueError, "Data is too short"):
            self.decoder.decode(b'')

    def test_encode_invalid_input(self):
        with self.assertRaises(ValueError):
            self.encoder.encode(-1)
        with self.assertRaises(ValueError):
            self.encoder.encode(0xFFFFFFFFFFFFFFFF + 1) # Too large
        with self.assertRaises(ValueError):
            self.encoder.encode("not an int")

class TestTransactionData(unittest.TestCase):
    def setUp(self):
        self.tx = TransactionData()
        self.txid_0 = "00" * 32
        self.txid_1 = "11" * 32
        self.script_sig_0 = "script_sig_for_test_0"
        self.script_sig_1 = "script_sig_for_test_1"
        self.script_pubkey_0 = "script_pubkey_for_test_0"
        self.script_pubkey_1 = "script_pubkey_for_test_1"

        # Capture print output
        self.held_stdout = sys.stdout
        self.new_stdout = io.StringIO()
        sys.stdout = self.new_stdout

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.held_stdout

    def test_add_input(self):
        self.tx.add_input(self.txid_0, 0, self.script_sig_0)
        self.assertEqual(len(self.tx.inputs), 1)
        expected_input = {
            "prev_txid": self.txid_0,
            "prev_vout": 0,
            "script_sig": self.script_sig_0,
            "sequence": 0xFFFFFFFF
        }
        self.assertEqual(self.tx.inputs[0], expected_input)
        # Check default sequence
        self.tx.add_input(self.txid_1, 1, self.script_sig_1, sequence=123)
        self.assertEqual(self.tx.inputs[1]["sequence"], 123)

    def test_add_output(self):
        self.tx.add_output(100000, self.script_pubkey_0)
        self.assertEqual(len(self.tx.outputs), 1)
        self.assertEqual(self.tx.outputs[0], (100000, self.script_pubkey_0))

    def test_get_input_details(self):
        self.tx.add_input(self.txid_0, 0, self.script_sig_0)
        self.tx.add_input(self.txid_1, 1, self.script_sig_1, sequence=123)
        details = self.tx.get_input_details()
        self.assertEqual(len(details), 2)
        self.assertEqual(details[0]["prev_txid"], self.txid_0)
        self.assertIn("--- Input Details", self.new_stdout.getvalue())

    def test_summarize_outputs_normal(self):
        self.tx.add_output(50000, self.script_pubkey_0)
        self.tx.add_output(30000, self.script_pubkey_1)
        total, count = self.tx.summarize_outputs()
        self.assertEqual(total, 80000)
        self.assertEqual(count, 2)
        self.assertIn("--- Summarizing Outputs", self.new_stdout.getvalue())
        self.assertIn("Including output", self.new_stdout.getvalue())

    def test_summarize_outputs_with_continue(self):
        self.tx.add_output(10000, self.script_pubkey_0)
        self.tx.add_output(500, self.script_pubkey_1) # Should be skipped
        self.tx.add_output(20000, self.script_pubkey_0)
        self.tx.add_output(-100, "invalid") # Should be skipped by continue
        total, count = self.tx.summarize_outputs(min_value=1000)
        self.assertEqual(total, 30000)
        self.assertEqual(count, 2)
        self.assertIn("Skipping output", self.new_stdout.getvalue())

    def test_summarize_outputs_with_break(self):
        self.tx.add_output(100000000, self.script_pubkey_0) # 1 BTC
        self.tx.add_output(950000000, self.script_pubkey_1) # 9.5 BTC - total now 10.5 BTC, should break
        self.tx.add_output(50000, self.script_pubkey_0) # Should not be reached
        total, count = self.tx.summarize_outputs()
        self.assertEqual(total, 1050000000) # 1 BTC + 9.5 BTC
        self.assertEqual(count, 2)
        self.assertIn("Total satoshis exceeded 1 Billion. Breaking summarization.", self.new_stdout.getvalue())
        self.assertNotIn("Skipping output 2", self.new_stdout.getvalue()) # Verify last output was not processed

    def test_update_metadata(self):
        self.tx.update_metadata({"fee": 100, "memo": "test"})
        self.assertEqual(self.tx.metadata, {"fee": 100, "memo": "test"})
        self.tx.update_metadata({"memo": "new test", "type": "payment"})
        self.assertEqual(self.tx.metadata, {"fee": 100, "memo": "new test", "type": "payment"})
        self.assertIn("Updated metadata", self.new_stdout.getvalue())

    def test_get_metadata_value(self):
        self.tx.update_metadata({"key1": "value1", "key2": 123})
        self.assertEqual(self.tx.get_metadata_value("key1"), "value1")
        self.assertEqual(self.tx.get_metadata_value("key2"), 123)
        self.assertIsNone(self.tx.get_metadata_value("non_existent_key"))
        self.assertEqual(self.tx.get_metadata_value("non_existent_key", "default_val"), "default_val")

    def test_get_transaction_header(self):
        self.tx.add_input(self.txid_0, 0, self.script_sig_0)
        self.tx.add_output(1000, self.script_pubkey_0)
        header = self.tx.get_transaction_header()
        self.assertEqual(header, (1, 1, 1, 0)) # Default version and lock_time for init

    def test_set_transaction_header(self):
        self.tx.set_transaction_header(2, 5, 6, 999)
        self.assertEqual(self.tx.version, 2)
        self.assertEqual(self.tx.lock_time, 999)
        # Check that num_inputs/outputs are not directly set as it's for demonstration of multiple assignment
        self.assertEqual(len(self.tx.inputs), 0)
        self.assertEqual(len(self.tx.outputs), 0)
        self.assertIn("Set header via multiple assignment", self.new_stdout.getvalue())

class TestUTXOSet(unittest.TestCase):
    def setUp(self):
        self.utxo_set = UTXOSet()
        self.utxo1 = ("tx1_id", 0, 10000)
        self.utxo2 = ("tx2_id", 1, 20000)
        self.utxo3 = ("tx3_id", 0, 5000)

        # Capture print output
        self.held_stdout = sys.stdout
        self.new_stdout = io.StringIO()
        sys.stdout = self.new_stdout

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.held_stdout

    def test_add_utxo(self):
        self.utxo_set.add_utxo(*self.utxo1)
        self.assertEqual(self.utxo_set.get_total_utxo_count(), 1)
        self.assertIn(self.utxo1, self.utxo_set.utxos)
        # Adding duplicate
        self.utxo_set.add_utxo(*self.utxo1)
        self.assertEqual(self.utxo_set.get_total_utxo_count(), 1) # Still 1

    def test_remove_utxo(self):
        self.utxo_set.add_utxo(*self.utxo1)
        self.assertTrue(self.utxo_set.remove_utxo(*self.utxo1))
        self.assertEqual(self.utxo_set.get_total_utxo_count(), 0)
        self.assertFalse(self.utxo_set.remove_utxo(*self.utxo2)) # Try removing non-existent
        self.assertIn("Removed UTXO", self.new_stdout.getvalue())
        self.assertIn("UTXO not found", self.new_stdout.getvalue())


    def test_get_balance(self):
        self.utxo_set.add_utxo(*self.utxo1) # 10000
        self.utxo_set.add_utxo(*self.utxo2) # 20000
        self.assertEqual(self.utxo_set.get_balance(), 30000)

    def test_find_sufficient_utxos(self):
        self.utxo_set.add_utxo(*self.utxo1) # 10000
        self.utxo_set.add_utxo(*self.utxo2) # 20000
        self.utxo_set.add_utxo(*self.utxo3) # 5000

        found = self.utxo_set.find_sufficient_utxos(25000)
        # Should find (tx2_id, 1, 20000) and (tx1_id, 0, 10000) or similar combination
        self.assertGreaterEqual(sum([utxo[2] for utxo in found]), 25000)
        self.assertLessEqual(sum([utxo[2] for utxo in found]), 35000) # Max total available
        self.assertIn("Found sufficient UTXOs", self.new_stdout.getvalue())

        found_none = self.utxo_set.find_sufficient_utxos(100000)
        self.assertEqual(found_none, set())
        self.assertIn("Could not find sufficient UTXOs", self.new_stdout.getvalue())


    def test_get_total_utxo_count(self):
        self.assertEqual(self.utxo_set.get_total_utxo_count(), 0)
        self.utxo_set.add_utxo(*self.utxo1)
        self.assertEqual(self.utxo_set.get_total_utxo_count(), 1)
        self.utxo_set.add_utxo(*self.utxo2)
        self.assertEqual(self.utxo_set.get_total_utxo_count(), 2)

    def test_is_subset_of(self):
        other_set = UTXOSet()
        other_set.add_utxo(*self.utxo1)
        other_set.add_utxo(*self.utxo2)

        self.utxo_set.add_utxo(*self.utxo1)
        self.assertTrue(self.utxo_set.is_subset_of(other_set))

        self.utxo_set.add_utxo(*self.utxo3)
        self.assertFalse(self.utxo_set.is_subset_of(other_set))

    def test_combine_utxos(self):
        self.utxo_set.add_utxo(*self.utxo1)
        other_set = UTXOSet()
        other_set.add_utxo(*self.utxo2)
        other_set.add_utxo(*self.utxo3)

        combined = self.utxo_set.combine_utxos(other_set)
        self.assertEqual(combined.get_total_utxo_count(), 3)
        self.assertIn(self.utxo1, combined.utxos)
        self.assertIn(self.utxo2, combined.utxos)
        self.assertIn(self.utxo3, combined.utxos)

    def test_find_common_utxos(self):
        self.utxo_set.add_utxo(*self.utxo1)
        self.utxo_set.add_utxo(*self.utxo2)
        other_set = UTXOSet()
        other_set.add_utxo(*self.utxo2)
        other_set.add_utxo(*self.utxo3)

        common = self.utxo_set.find_common_utxos(other_set)
        self.assertEqual(common.get_total_utxo_count(), 1)
        self.assertIn(self.utxo2, common.utxos)


class TestBlockHeaderGenerator(unittest.TestCase):
    def setUp(self):
        self.prev_hash = "00" * 32
        self.merkle_root = "11" * 32
        self.timestamp = 1678886400
        self.bits = 0x1d00ffff

        # Capture print output
        self.held_stdout = sys.stdout
        self.new_stdout = io.StringIO()
        sys.stdout = self.new_stdout

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.held_stdout

    def test_generator_yields_correct_structure(self):
        gen = generate_block_headers(self.prev_hash, self.merkle_root, self.timestamp, self.bits, start_nonce=0, max_attempts=1)
        header = next(gen)
        self.assertIsInstance(header, dict)
        self.assertIn("version", header)
        self.assertIn("prev_block_hash", header)
        self.assertIn("merkle_root", header)
        self.assertIn("timestamp", header)
        self.assertIn("bits", header)
        self.assertIn("nonce", header)
        self.assertEqual(header["nonce"], 0)

    def test_generator_increments_nonce(self):
        gen = generate_block_headers(self.prev_hash, self.merkle_root, self.timestamp, self.bits, start_nonce=10, max_attempts=3)
        header1 = next(gen)
        header2 = next(gen)
        header3 = next(gen)
        self.assertEqual(header1["nonce"], 10)
        self.assertEqual(header2["nonce"], 11)
        self.assertEqual(header3["nonce"], 12)

    def test_generator_respects_max_attempts(self):
        gen = generate_block_headers(self.prev_hash, self.merkle_root, self.timestamp, self.bits, max_attempts=5)
        headers = list(gen) # Consume all generated items
        self.assertEqual(len(headers), 5)
        with self.assertRaises(StopIteration):
            next(gen) # Should be exhausted

    def test_generator_breaks_early(self):
        gen = generate_block_headers(self.prev_hash, self.merkle_root, self.timestamp, self.bits, max_attempts=10)
        count = 0
        for header in gen:
            count += 1
            if count == 3:
                break # Simulate early stopping
        self.assertEqual(count, 3)

    def test_generator_prints_progress(self):
        gen = generate_block_headers(self.prev_hash, self.merkle_root, self.timestamp, self.bits, max_attempts=101)
        list(gen) # Consume fully
        output = self.new_stdout.getvalue()
        self.assertIn("--- Generating Block Headers", output)
        self.assertIn("Attempt 1:", output)
        self.assertIn("... 100 attempts made ...", output)
        self.assertIn("Attempt 101:", output)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

